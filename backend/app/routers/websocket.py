import asyncio
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models import (
    AudioOutputEvent,
    ErrorEvent,
    SessionStartedEvent,
    SessionStoppedEvent,
    SlideChangedEvent,
    TranscriptEvent,
)
from app.services import (
    FunctionHandler,
    PresentationSession,
    RealtimeClient,
    build_session_config,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:

    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.session = PresentationSession()
        self.function_handler = FunctionHandler(self.session)
        self.realtime_client = RealtimeClient()
        self._running = False
        self._openai_connected = asyncio.Event()
        self._ending_presentation = False

    async def send_to_client(self, event: dict[str, Any]) -> None:
        try:
            await self.websocket.send_json(event)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")

    async def handle_openai_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "")

        if event_type == "response.audio.delta":
            audio_data = event.get("delta", "")
            if audio_data:
                await self.send_to_client(
                    AudioOutputEvent(audio=audio_data).model_dump()
                )

        elif event_type == "response.audio.done":
            await self.send_to_client({"type": "audio.done"})

        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            if transcript:
                await self.send_to_client(
                    TranscriptEvent(
                        text=transcript, is_final=True, speaker="user"
                    ).model_dump()
                )

        elif event_type == "response.audio_transcript.delta":
            delta = event.get("delta", "")
            if delta:
                await self.send_to_client(
                    TranscriptEvent(
                        text=delta, is_final=False, speaker="ai"
                    ).model_dump()
                )

        elif event_type == "response.function_call_arguments.done":
            await self._handle_function_call(event)

        elif event_type == "session.created":
            logger.info("OpenAI session created")

        elif event_type == "session.updated":
            logger.info("OpenAI session updated")

        elif event_type == "error":
            error_msg = event.get("error", {}).get("message", "Unknown error")
            logger.error(f"OpenAI error: {error_msg}")
            await self.send_to_client(
                ErrorEvent(message=error_msg, code="openai_error").model_dump()
            )

        elif event_type == "response.done":
            self.session.is_ai_speaking = False
            # If ending presentation, stop after AI finishes farewell
            if self._ending_presentation:
                logger.info("AI finished farewell - stopping session")
                await asyncio.sleep(1)  # Brief pause after farewell
                await self._stop_session()

        elif event_type == "input_audio_buffer.speech_started":
            self.session.is_ai_speaking = False
            logger.info("User started speaking - interrupting AI")
            # Cancel any ongoing AI response to allow interruption
            await self.realtime_client.cancel_response()
            # Notify frontend that AI stopped speaking
            await self.send_to_client({"type": "audio.interrupted"})

    async def _handle_function_call(self, event: dict[str, Any]) -> None:
        call_id = event.get("call_id", "")
        name = event.get("name", "")
        arguments = event.get("arguments", "{}")

        logger.info(f"Function call: {name}")

        # Process the function call
        result, slide = self.function_handler.handle_function_call(name, arguments)

        # If slide changed, notify frontend
        if slide:
            slide_event = SlideChangedEvent(
                slide_id=slide.id,
                title=slide.title,
                content=slide.content,
                narration=slide.narration,
                total_slides=self.session.total_slides,
                has_next=self.session.has_next,
                has_previous=self.session.has_previous,
            )
            await self.send_to_client(slide_event.model_dump())

        await self.realtime_client.send_function_result(call_id, result)

        # If end_presentation was called, set flag to stop after AI finishes speaking
        if result.get("action") == "end_presentation":
            logger.info("End presentation requested - will stop after AI farewell")
            self._ending_presentation = True

    async def handle_client_event(self, data: dict[str, Any]) -> None:
        """Process events from the frontend."""
        event_type = data.get("type", "")

        if event_type == "session.start":
            await self._start_session()

        elif event_type == "session.stop":
            await self._stop_session()

        elif event_type == "audio.input":
            # Forward audio to OpenAI
            audio = data.get("audio", "")
            if audio:
                await self.realtime_client.send_audio(audio)

        elif event_type == "slide.navigate":
            direction = data.get("direction")
            if direction == "next":
                slide = self.session.next_slide()
            elif direction == "prev":
                slide = self.session.previous_slide()
            else:
                slide = None

            if slide:
                await self._send_slide_changed()

        elif event_type == "slide.goto":
            slide_id = data.get("slide_id")
            if slide_id:
                slide = self.session.go_to_slide(slide_id)
                if slide:
                    await self._send_slide_changed()

        elif event_type == "response.cancel":
            # User wants to interrupt AI
            await self.realtime_client.cancel_response()

    async def _start_session(self) -> None:
        try:
            await self.realtime_client.connect()
            self._openai_connected.set()

            config = build_session_config()
            await self.realtime_client.configure_session(config)

            self.session.is_presenting = True

            await self.send_to_client(
                SessionStartedEvent(session_id=self.session.session_id).model_dump()
            )
            await self._send_slide_changed()

            await self.realtime_client.create_response()

            logger.info(f"Session started: {self.session.session_id}")

        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            await self.send_to_client(
                ErrorEvent(message=str(e), code="session_start_failed").model_dump()
            )

    async def _stop_session(self) -> None:
        self.session.is_presenting = False
        self._openai_connected.clear()
        await self.realtime_client.disconnect()
        await self.send_to_client(SessionStoppedEvent().model_dump())
        logger.info(f"Session stopped: {self.session.session_id}")

    async def _send_slide_changed(self) -> None:
        slide = self.session.current_slide
        await self.send_to_client(
            SlideChangedEvent(
                slide_id=slide.id,
                title=slide.title,
                content=slide.content,
                narration=slide.narration,
                total_slides=self.session.total_slides,
                has_next=self.session.has_next,
                has_previous=self.session.has_previous,
            ).model_dump()
        )

    async def run(self) -> None:
        """Main loop: handle client messages and forward OpenAI responses."""
        self._running = True
        await self._send_slide_changed()

        async def forward_openai_to_client() -> None:
            """Forward events from OpenAI to the frontend."""
            try:
                # Wait for OpenAI connection before starting to receive
                await self._openai_connected.wait()
                async for event in self.realtime_client.receive():
                    if not self._running:
                        break
                    await self.handle_openai_event(event)
            except Exception as e:
                if self._running:
                    logger.error(f"OpenAI receiver error: {e}")
            finally:
                self._running = False

        async def receive_from_client() -> None:
            try:
                while self._running:
                    data = await self.websocket.receive_json()
                    await self.handle_client_event(data)
            except WebSocketDisconnect:
                logger.info("Client disconnected")
            except Exception as e:
                if self._running:
                    logger.error(f"Client receiver error: {e}")
            finally:
                self._running = False

        await asyncio.gather(
            receive_from_client(),
            forward_openai_to_client(),
            return_exceptions=True,
        )

    async def cleanup(self) -> None:
        self._running = False
        self._openai_connected.set()  # Unblock waiting coroutine
        if self.realtime_client.is_connected:
            await self.realtime_client.disconnect()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for voice presentation."""
    await websocket.accept()
    logger.info("Client connected")

    manager = ConnectionManager(websocket)

    try:
        await manager.run()
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.cleanup()
        logger.info("Connection cleaned up")
