import json
import uuid

import pytest

from app.data.slides import SLIDES, get_total_slides
from app.services.session_manager import FunctionHandler, PresentationSession


class TestPresentationSessionInit:
    """Tests for PresentationSession initialization."""

    def test_session_has_unique_id(self) -> None:
        """Each session should have a unique UUID."""
        session1 = PresentationSession()
        session2 = PresentationSession()

        assert session1.session_id != session2.session_id
        # Validate UUID format
        uuid.UUID(session1.session_id)
        uuid.UUID(session2.session_id)

    def test_session_starts_at_slide_1(self, session: PresentationSession) -> None:
        """Session should start at slide 1."""
        assert session.current_slide_id == 1

    def test_session_starts_not_presenting(self, session: PresentationSession) -> None:
        """Session should not be presenting initially."""
        assert session.is_presenting is False

    def test_session_starts_ai_not_speaking(self, session: PresentationSession) -> None:
        """AI should not be speaking initially."""
        assert session.is_ai_speaking is False


class TestPresentationSessionProperties:
    """Tests for PresentationSession properties."""

    def test_current_slide_returns_correct_slide(self, session: PresentationSession) -> None:
        """current_slide should return the slide matching current_slide_id."""
        assert session.current_slide.id == 1
        session.current_slide_id = 3
        assert session.current_slide.id == 3

    def test_current_slide_fallback_on_invalid_id(self, session: PresentationSession) -> None:
        """current_slide should fallback to first slide on invalid ID."""
        session.current_slide_id = 999
        assert session.current_slide.id == SLIDES[0].id

    def test_total_slides_matches_data(self, session: PresentationSession) -> None:
        """total_slides should match actual slide count."""
        assert session.total_slides == get_total_slides()
        assert session.total_slides == len(SLIDES)

    def test_has_next_on_first_slide(self, session: PresentationSession) -> None:
        """Should have next slide when on first slide."""
        session.current_slide_id = 1
        assert session.has_next is True

    def test_has_next_on_last_slide(self, session: PresentationSession) -> None:
        """Should not have next slide when on last slide."""
        session.current_slide_id = session.total_slides
        assert session.has_next is False

    def test_has_previous_on_first_slide(self, session: PresentationSession) -> None:
        """Should not have previous slide when on first slide."""
        session.current_slide_id = 1
        assert session.has_previous is False

    def test_has_previous_on_last_slide(self, session: PresentationSession) -> None:
        """Should have previous slide when on last slide."""
        session.current_slide_id = session.total_slides
        assert session.has_previous is True

    def test_has_previous_on_middle_slide(self, session: PresentationSession) -> None:
        """Should have previous slide when on middle slide."""
        session.current_slide_id = 3
        assert session.has_previous is True
        assert session.has_next is True


class TestSlideNavigation:
    """Tests for slide navigation methods."""

    def test_go_to_valid_slide(self, session: PresentationSession) -> None:
        """go_to_slide should navigate to valid slide."""
        slide = session.go_to_slide(3)

        assert slide is not None
        assert slide.id == 3
        assert session.current_slide_id == 3

    def test_go_to_first_slide(self, session: PresentationSession) -> None:
        """go_to_slide should navigate to first slide."""
        session.current_slide_id = 5
        slide = session.go_to_slide(1)

        assert slide is not None
        assert slide.id == 1
        assert session.current_slide_id == 1

    def test_go_to_last_slide(self, session: PresentationSession) -> None:
        """go_to_slide should navigate to last slide."""
        last_id = session.total_slides
        slide = session.go_to_slide(last_id)

        assert slide is not None
        assert slide.id == last_id

    def test_go_to_invalid_slide_zero(self, session: PresentationSession) -> None:
        """go_to_slide should return None for slide 0."""
        original_id = session.current_slide_id
        slide = session.go_to_slide(0)

        assert slide is None
        assert session.current_slide_id == original_id  # Unchanged

    def test_go_to_invalid_slide_negative(self, session: PresentationSession) -> None:
        """go_to_slide should return None for negative ID."""
        original_id = session.current_slide_id
        slide = session.go_to_slide(-1)

        assert slide is None
        assert session.current_slide_id == original_id

    def test_go_to_invalid_slide_too_high(self, session: PresentationSession) -> None:
        """go_to_slide should return None for ID beyond total."""
        original_id = session.current_slide_id
        slide = session.go_to_slide(session.total_slides + 1)

        assert slide is None
        assert session.current_slide_id == original_id

    def test_next_slide_advances(self, session: PresentationSession) -> None:
        """next_slide should advance by one."""
        session.current_slide_id = 1
        slide = session.next_slide()

        assert slide is not None
        assert slide.id == 2
        assert session.current_slide_id == 2

    def test_next_slide_on_last_returns_none(self, session: PresentationSession) -> None:
        """next_slide should return None on last slide."""
        session.current_slide_id = session.total_slides
        slide = session.next_slide()

        assert slide is None
        assert session.current_slide_id == session.total_slides  # Unchanged

    def test_previous_slide_goes_back(self, session: PresentationSession) -> None:
        """previous_slide should go back by one."""
        session.current_slide_id = 3
        slide = session.previous_slide()

        assert slide is not None
        assert slide.id == 2
        assert session.current_slide_id == 2

    def test_previous_slide_on_first_returns_none(self, session: PresentationSession) -> None:
        """previous_slide should return None on first slide."""
        session.current_slide_id = 1
        slide = session.previous_slide()

        assert slide is None
        assert session.current_slide_id == 1  # Unchanged

    def test_navigation_sequence(self, session: PresentationSession) -> None:
        """Test a sequence of navigation operations."""
        assert session.current_slide_id == 1

        session.next_slide()
        assert session.current_slide_id == 2

        session.next_slide()
        assert session.current_slide_id == 3

        session.previous_slide()
        assert session.current_slide_id == 2

        session.go_to_slide(5)
        assert session.current_slide_id == 5

        session.go_to_slide(1)
        assert session.current_slide_id == 1


class TestGetSlideInfo:
    """Tests for get_slide_info method."""

    def test_get_slide_info_returns_dict(self, session: PresentationSession) -> None:
        """get_slide_info should return a dictionary."""
        info = session.get_slide_info()
        assert isinstance(info, dict)

    def test_get_slide_info_has_required_keys(self, session: PresentationSession) -> None:
        """get_slide_info should have all required keys."""
        info = session.get_slide_info()

        required_keys = {
            "slide_id", "title", "content", "narration",
            "total_slides", "has_next", "has_previous"
        }
        assert required_keys == set(info.keys())

    def test_get_slide_info_reflects_current_slide(self, session: PresentationSession) -> None:
        """get_slide_info should reflect current slide state."""
        session.current_slide_id = 3
        info = session.get_slide_info()

        assert info["slide_id"] == 3
        assert info["has_next"] is True
        assert info["has_previous"] is True

    def test_get_slide_info_on_first_slide(self, session: PresentationSession) -> None:
        """get_slide_info on first slide."""
        session.current_slide_id = 1
        info = session.get_slide_info()

        assert info["slide_id"] == 1
        assert info["has_previous"] is False
        assert info["has_next"] is True

    def test_get_slide_info_on_last_slide(self, session: PresentationSession) -> None:
        """get_slide_info on last slide."""
        session.current_slide_id = session.total_slides
        info = session.get_slide_info()

        assert info["slide_id"] == session.total_slides
        assert info["has_previous"] is True
        assert info["has_next"] is False


class TestFunctionHandlerNavigate:
    """Tests for FunctionHandler navigate_to_slide."""

    def test_navigate_to_valid_slide(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should work with valid slide_id."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 3, "reason": "User asked about applications"})
        )

        assert result["success"] is True
        assert result["navigated_to"] == 3
        assert slide is not None
        assert slide.id == 3

    def test_navigate_without_reason(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should work without reason."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 2})
        )

        assert result["success"] is True
        assert result["reason"] == "User requested"  # Default
        assert slide is not None

    def test_navigate_missing_slide_id(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should fail without slide_id."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"reason": "No slide_id"})
        )

        assert "error" in result
        assert slide is None

    def test_navigate_invalid_slide_id(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should fail with invalid slide_id."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 999})
        )

        assert result["success"] is False
        assert "error" in result
        assert slide is None

    def test_navigate_with_empty_arguments(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should fail with empty arguments."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            ""
        )

        assert "error" in result
        assert slide is None

    def test_navigate_with_invalid_json(self, function_handler: FunctionHandler) -> None:
        """navigate_to_slide should handle invalid JSON gracefully."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            "not valid json {"
        )

        assert "error" in result
        assert slide is None


class TestFunctionHandlerGetInfo:
    """Tests for FunctionHandler get_current_slide_info."""

    def test_get_current_slide_info(self, function_handler: FunctionHandler) -> None:
        """get_current_slide_info should return slide info."""
        result, slide = function_handler.handle_function_call(
            "get_current_slide_info",
            ""
        )

        assert "slide_id" in result
        assert "title" in result
        assert slide is None  # This function doesn't change slides

    def test_get_info_after_navigation(self, function_handler: FunctionHandler) -> None:
        """get_current_slide_info should reflect navigation."""
        function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 4})
        )

        result, _ = function_handler.handle_function_call(
            "get_current_slide_info",
            ""
        )

        assert result["slide_id"] == 4


class TestFunctionHandlerEndPresentation:
    """Tests for FunctionHandler end_presentation."""

    def test_end_presentation_basic(self, function_handler: FunctionHandler) -> None:
        """end_presentation should end the session."""
        function_handler.session.is_presenting = True

        result, slide = function_handler.handle_function_call(
            "end_presentation",
            json.dumps({"farewell_message": "Goodbye!"})
        )

        assert result["success"] is True
        assert result["action"] == "end_presentation"
        assert result["farewell"] == "Goodbye!"
        assert function_handler.session.is_presenting is False
        assert slide is None

    def test_end_presentation_default_farewell(self, function_handler: FunctionHandler) -> None:
        """end_presentation should use default farewell if not provided."""
        result, _ = function_handler.handle_function_call(
            "end_presentation",
            ""
        )

        assert result["success"] is True
        assert result["farewell"] == "Thank you for attending!"

    def test_end_presentation_empty_args(self, function_handler: FunctionHandler) -> None:
        """end_presentation should work with empty JSON object."""
        result, _ = function_handler.handle_function_call(
            "end_presentation",
            json.dumps({})
        )

        assert result["success"] is True


class TestFunctionHandlerUnknownFunction:
    """Tests for unknown function handling."""

    def test_unknown_function(self, function_handler: FunctionHandler) -> None:
        """Unknown function should return error."""
        result, slide = function_handler.handle_function_call(
            "unknown_function",
            "{}"
        )

        assert "error" in result
        assert "Unknown function" in result["error"]
        assert slide is None

    def test_empty_function_name(self, function_handler: FunctionHandler) -> None:
        """Empty function name should return error."""
        result, slide = function_handler.handle_function_call(
            "",
            "{}"
        )

        assert "error" in result
        assert slide is None


class TestFunctionHandlerEdgeCases:
    """Edge case tests for FunctionHandler."""

    def test_navigate_boundary_first_slide(self, function_handler: FunctionHandler) -> None:
        """Navigate to first slide boundary."""
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 1})
        )

        assert result["success"] is True
        assert slide.id == 1

    def test_navigate_boundary_last_slide(self, function_handler: FunctionHandler) -> None:
        """Navigate to last slide boundary."""
        last_id = function_handler.session.total_slides
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": last_id})
        )

        assert result["success"] is True
        assert slide.id == last_id

    def test_navigate_just_beyond_boundary(self, function_handler: FunctionHandler) -> None:
        """Navigate to slide just beyond valid range."""
        beyond_id = function_handler.session.total_slides + 1
        result, slide = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": beyond_id})
        )

        assert result["success"] is False
        assert slide is None

    def test_multiple_navigations(self, function_handler: FunctionHandler) -> None:
        """Multiple navigations should work correctly."""
        for slide_id in [1, 3, 5, 2, 4]:
            result, slide = function_handler.handle_function_call(
                "navigate_to_slide",
                json.dumps({"slide_id": slide_id})
            )
            assert result["success"] is True
            assert slide.id == slide_id
            assert function_handler.session.current_slide_id == slide_id

    def test_narration_hint_truncation(self, function_handler: FunctionHandler) -> None:
        """Navigate result should include truncated narration hint."""
        result, _ = function_handler.handle_function_call(
            "navigate_to_slide",
            json.dumps({"slide_id": 1})
        )

        assert "narration_hint" in result
        assert result["narration_hint"].endswith("...")
        assert len(result["narration_hint"]) <= 204  # 200 chars + "..."
