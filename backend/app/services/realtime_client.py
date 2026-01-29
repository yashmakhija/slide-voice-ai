import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Callable

import websockets
from websockets.asyncio.client import ClientConnection

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RealtimeClient:

    def __init__(self) -> None:
        self._ws: ClientConnection | None = None
        self._is_connected: bool = False
        self._on_message_callback: Callable[[dict[str, Any]], None] | None = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected and self._ws is not None

    async def connect(self) -> None:
        url = settings.openai_realtime_ws_url
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        logger.info(f"Connecting to OpenAI Realtime API: {url}")

        try:
            self._ws = await websockets.connect(
                url,
                additional_headers=headers,
            )
            self._is_connected = True
            logger.info("Connected to OpenAI Realtime API")
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            self._is_connected = False
            raise

    async def disconnect(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
            self._is_connected = False
            logger.info("Disconnected from OpenAI Realtime API")

    async def send(self, event: dict[str, Any]) -> None:
        if not self._ws:
            raise RuntimeError("Not connected to OpenAI")

        message = json.dumps(event)
        await self._ws.send(message)
        logger.debug(f"Sent event: {event.get('type')}")

    async def receive(self) -> AsyncGenerator[dict[str, Any], None]:
        if not self._ws:
            raise RuntimeError("Not connected to OpenAI")

        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                event = json.loads(message)
                logger.debug(f"Received event: {event.get('type')}")
                yield event
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI connection closed")
            self._is_connected = False

    async def configure_session(self, session_config: dict[str, Any]) -> None:
        event = {
            "type": "session.update",
            "session": session_config,
        }
        await self.send(event)
        logger.info("Session configured")

    async def send_audio(self, audio_base64: str) -> None:
        event = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64,
        }
        await self.send(event)

    async def commit_audio(self) -> None:
        event = {"type": "input_audio_buffer.commit"}
        await self.send(event)

    async def create_response(self) -> None:
        event = {"type": "response.create"}
        await self.send(event)

    async def cancel_response(self) -> None:
        event = {"type": "response.cancel"}
        await self.send(event)

    async def send_function_result(
        self, call_id: str, result: dict[str, Any]
    ) -> None:
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result),
            },
        }
        await self.send(event)
        await self.create_response()
