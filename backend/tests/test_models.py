import pytest
from pydantic import ValidationError

from app.models import Slide
from app.models.events import (
    AudioInputEvent,
    AudioOutputEvent,
    ErrorEvent,
    GoToSlideEvent,
    NavigateEvent,
    SessionStartedEvent,
    SessionStoppedEvent,
    SlideChangedEvent,
    StartSessionEvent,
    StopSessionEvent,
    TranscriptEvent,
)


class TestSlideModel:
    """Tests for Slide model validation."""

    def test_valid_slide(self) -> None:
        """Valid slide should be created successfully."""
        slide = Slide(
            id=1,
            title="Test Slide",
            content=["Point 1", "Point 2"],
            narration="This is the narration.",
            iconName="brain"
        )

        assert slide.id == 1
        assert slide.title == "Test Slide"
        assert len(slide.content) == 2
        assert slide.iconName == "brain"

    def test_slide_default_icon(self) -> None:
        """Slide should have default iconName."""
        slide = Slide(
            id=1,
            title="Test",
            content=[],
            narration="Narration"
        )

        assert slide.iconName == "layers"

    def test_slide_empty_content_list(self) -> None:
        """Slide can have empty content list."""
        slide = Slide(
            id=1,
            title="Test",
            content=[],
            narration="Narration"
        )

        assert slide.content == []

    def test_slide_invalid_id_zero(self) -> None:
        """Slide ID must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            Slide(id=0, title="Test", content=[], narration="Narration")

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_slide_invalid_id_negative(self) -> None:
        """Slide ID cannot be negative."""
        with pytest.raises(ValidationError):
            Slide(id=-1, title="Test", content=[], narration="Narration")

    def test_slide_empty_title(self) -> None:
        """Slide title cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Slide(id=1, title="", content=[], narration="Narration")

        assert "min_length" in str(exc_info.value).lower() or "at least 1" in str(exc_info.value).lower()

    def test_slide_empty_narration(self) -> None:
        """Slide narration cannot be empty."""
        with pytest.raises(ValidationError):
            Slide(id=1, title="Test", content=[], narration="")

    def test_slide_missing_required_field(self) -> None:
        """Slide requires all mandatory fields."""
        with pytest.raises(ValidationError):
            Slide(id=1, title="Test")  # Missing narration

    def test_slide_serialization(self) -> None:
        """Slide should serialize correctly."""
        slide = Slide(
            id=1,
            title="Test",
            content=["Item"],
            narration="Narration",
            iconName="rocket"
        )

        data = slide.model_dump()
        assert data["id"] == 1
        assert data["iconName"] == "rocket"


class TestClientEventModels:
    """Tests for client event models."""

    def test_start_session_event(self) -> None:
        """StartSessionEvent should have correct type."""
        event = StartSessionEvent()
        assert event.type == "session.start"

    def test_stop_session_event(self) -> None:
        """StopSessionEvent should have correct type."""
        event = StopSessionEvent()
        assert event.type == "session.stop"

    def test_audio_input_event(self) -> None:
        """AudioInputEvent should validate audio field."""
        event = AudioInputEvent(audio="base64encodeddata")
        assert event.type == "audio.input"
        assert event.audio == "base64encodeddata"

    def test_audio_input_event_empty_audio(self) -> None:
        """AudioInputEvent requires non-empty audio."""
        # Empty string should still be allowed by model, validation is semantic
        event = AudioInputEvent(audio="")
        assert event.audio == ""

    def test_navigate_event_next(self) -> None:
        """NavigateEvent should accept 'next' direction."""
        event = NavigateEvent(direction="next")
        assert event.type == "slide.navigate"
        assert event.direction == "next"

    def test_navigate_event_prev(self) -> None:
        """NavigateEvent should accept 'prev' direction."""
        event = NavigateEvent(direction="prev")
        assert event.direction == "prev"

    def test_navigate_event_invalid_direction(self) -> None:
        """NavigateEvent should reject invalid direction."""
        with pytest.raises(ValidationError):
            NavigateEvent(direction="invalid")

    def test_goto_slide_event(self) -> None:
        """GoToSlideEvent should validate slide_id."""
        event = GoToSlideEvent(slide_id=3)
        assert event.type == "slide.goto"
        assert event.slide_id == 3

    def test_goto_slide_event_invalid_id(self) -> None:
        """GoToSlideEvent should reject invalid slide_id."""
        with pytest.raises(ValidationError):
            GoToSlideEvent(slide_id=0)

        with pytest.raises(ValidationError):
            GoToSlideEvent(slide_id=-1)


class TestServerEventModels:
    """Tests for server event models."""

    def test_session_started_event(self) -> None:
        """SessionStartedEvent should include session_id."""
        event = SessionStartedEvent(session_id="test-uuid-123")
        assert event.type == "session.started"
        assert event.session_id == "test-uuid-123"

    def test_session_stopped_event(self) -> None:
        """SessionStoppedEvent should have correct type."""
        event = SessionStoppedEvent()
        assert event.type == "session.stopped"

    def test_audio_output_event(self) -> None:
        """AudioOutputEvent should include audio data."""
        event = AudioOutputEvent(audio="base64data")
        assert event.type == "audio.output"
        assert event.audio == "base64data"

    def test_slide_changed_event(self) -> None:
        """SlideChangedEvent should include all slide info."""
        event = SlideChangedEvent(
            slide_id=2,
            title="Test Title",
            content=["Item 1", "Item 2"],
            narration="Test narration",
            total_slides=5,
            has_next=True,
            has_previous=True
        )

        assert event.type == "slide.changed"
        assert event.slide_id == 2
        assert event.title == "Test Title"
        assert len(event.content) == 2
        assert event.total_slides == 5
        assert event.has_next is True
        assert event.has_previous is True

    def test_slide_changed_event_boundaries(self) -> None:
        """SlideChangedEvent for first and last slides."""
        # First slide
        first = SlideChangedEvent(
            slide_id=1,
            title="First",
            content=[],
            narration="N",
            total_slides=5,
            has_next=True,
            has_previous=False
        )
        assert first.has_previous is False

        # Last slide
        last = SlideChangedEvent(
            slide_id=5,
            title="Last",
            content=[],
            narration="N",
            total_slides=5,
            has_next=False,
            has_previous=True
        )
        assert last.has_next is False

    def test_transcript_event_user(self) -> None:
        """TranscriptEvent for user speech."""
        event = TranscriptEvent(
            text="Hello, can you explain this?",
            is_final=True,
            speaker="user"
        )

        assert event.type == "transcript"
        assert event.speaker == "user"
        assert event.is_final is True

    def test_transcript_event_ai(self) -> None:
        """TranscriptEvent for AI speech."""
        event = TranscriptEvent(
            text="Let me explain...",
            is_final=False,
            speaker="ai"
        )

        assert event.speaker == "ai"
        assert event.is_final is False

    def test_transcript_event_invalid_speaker(self) -> None:
        """TranscriptEvent should reject invalid speaker."""
        with pytest.raises(ValidationError):
            TranscriptEvent(text="Test", speaker="unknown")

    def test_error_event(self) -> None:
        """ErrorEvent should include message and optional code."""
        event = ErrorEvent(message="Something went wrong", code="test_error")
        assert event.type == "error"
        assert event.message == "Something went wrong"
        assert event.code == "test_error"

    def test_error_event_no_code(self) -> None:
        """ErrorEvent code is optional."""
        event = ErrorEvent(message="Error occurred")
        assert event.code is None


class TestEventSerialization:
    """Tests for event model serialization."""

    def test_slide_changed_serialization(self) -> None:
        """SlideChangedEvent should serialize to dict correctly."""
        event = SlideChangedEvent(
            slide_id=1,
            title="Title",
            content=["A", "B"],
            narration="Narration",
            total_slides=5,
            has_next=True,
            has_previous=False
        )

        data = event.model_dump()

        assert data["type"] == "slide.changed"
        assert isinstance(data["content"], list)
        assert data["has_next"] is True

    def test_event_json_serialization(self) -> None:
        """Events should serialize to JSON."""
        event = SessionStartedEvent(session_id="test-123")
        json_str = event.model_dump_json()

        assert "session.started" in json_str
        assert "test-123" in json_str

    def test_navigate_event_serialization(self) -> None:
        """NavigateEvent should serialize direction correctly."""
        event = NavigateEvent(direction="next")
        data = event.model_dump()

        assert data["direction"] == "next"
        assert data["type"] == "slide.navigate"
