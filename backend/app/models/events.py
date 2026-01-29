from typing import Literal, Union

from pydantic import BaseModel, Field


class StartSessionEvent(BaseModel):

    type: Literal["session.start"] = "session.start"


class StopSessionEvent(BaseModel):

    type: Literal["session.stop"] = "session.stop"


class AudioInputEvent(BaseModel):

    type: Literal["audio.input"] = "audio.input"
    audio: str = Field(..., description="Base64 encoded PCM16 audio data")


class NavigateEvent(BaseModel):

    type: Literal["slide.navigate"] = "slide.navigate"
    direction: Literal["next", "prev"]


class GoToSlideEvent(BaseModel):

    type: Literal["slide.goto"] = "slide.goto"
    slide_id: int = Field(..., ge=1)


ClientEvent = Union[
    StartSessionEvent,
    StopSessionEvent,
    AudioInputEvent,
    NavigateEvent,
    GoToSlideEvent,
]


class SessionStartedEvent(BaseModel):

    type: Literal["session.started"] = "session.started"
    session_id: str


class SessionStoppedEvent(BaseModel):

    type: Literal["session.stopped"] = "session.stopped"


class AudioOutputEvent(BaseModel):

    type: Literal["audio.output"] = "audio.output"
    audio: str = Field(..., description="Base64 encoded PCM16 audio data")


class AudioDoneEvent(BaseModel):

    type: Literal["audio.done"] = "audio.done"


class SlideChangedEvent(BaseModel):

    type: Literal["slide.changed"] = "slide.changed"
    slide_id: int
    title: str
    content: list[str]
    narration: str
    total_slides: int
    has_next: bool
    has_previous: bool


class TranscriptEvent(BaseModel):

    type: Literal["transcript"] = "transcript"
    text: str
    is_final: bool = False
    speaker: Literal["user", "ai"]


class ErrorEvent(BaseModel):

    type: Literal["error"] = "error"
    message: str
    code: str | None = None


class ConnectionStatusEvent(BaseModel):

    type: Literal["connection.status"] = "connection.status"
    status: Literal["connecting", "connected", "disconnected", "error"]
    message: str | None = None


# Union type for all server events
ServerEvent = Union[
    SessionStartedEvent,
    SessionStoppedEvent,
    AudioOutputEvent,
    AudioDoneEvent,
    SlideChangedEvent,
    TranscriptEvent,
    ErrorEvent,
    ConnectionStatusEvent,
]
