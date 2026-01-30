"""
Session manager for presentation state.

Tracks:
- Current slide
- Session state
- Handles function calls from AI
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.data.slides import SLIDES, get_slide_by_id, get_total_slides
from app.models import Slide

logger = logging.getLogger(__name__)


@dataclass
class PresentationSession:

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_slide_id: int = 1
    is_presenting: bool = False
    is_ai_speaking: bool = False

    @property
    def current_slide(self) -> Slide:
        slide = get_slide_by_id(self.current_slide_id)
        if slide is None:
            return SLIDES[0]
        return slide

    @property
    def total_slides(self) -> int:
        return get_total_slides()

    @property
    def has_next(self) -> bool:
        return self.current_slide_id < self.total_slides

    @property
    def has_previous(self) -> bool:
        return self.current_slide_id > 1

    def go_to_slide(self, slide_id: int) -> Slide | None:
        if 1 <= slide_id <= self.total_slides:
            self.current_slide_id = slide_id
            logger.info(f"Navigated to slide {slide_id}: {self.current_slide.title}")
            return self.current_slide
        logger.warning(f"Invalid slide_id: {slide_id}")
        return None

    def next_slide(self) -> Slide | None:
        if self.has_next:
            return self.go_to_slide(self.current_slide_id + 1)
        return None

    def previous_slide(self) -> Slide | None:
        if self.has_previous:
            return self.go_to_slide(self.current_slide_id - 1)
        return None

    def get_slide_info(self) -> dict[str, Any]:
        slide = self.current_slide
        return {
            "slide_id": slide.id,
            "title": slide.title,
            "content": slide.content,
            "narration": slide.narration,
            "total_slides": self.total_slides,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


class FunctionHandler:

    def __init__(self, session: PresentationSession) -> None:
        self.session = session

    def handle_function_call(
        self, function_name: str, arguments: str
    ) -> tuple[dict[str, Any], Slide | None]:
        """
        Handle a function call from the AI.

        Returns:
            Tuple of (result_dict, slide_if_changed)
        """
        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError:
            args = {}

        logger.info(f"Function call: {function_name}({args})")

        if function_name == "navigate_to_slide":
            return self._handle_navigate(args)
        elif function_name == "get_current_slide_info":
            return self._handle_get_info()
        elif function_name == "end_presentation":
            return self._handle_end_presentation(args)
        else:
            logger.warning(f"Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}, None

    def _handle_navigate(
        self, args: dict[str, Any]
    ) -> tuple[dict[str, Any], Slide | None]:
        """Handle navigate_to_slide function call."""
        slide_id = args.get("slide_id")
        reason = args.get("reason", "User requested")

        if slide_id is None:
            return {"error": "slide_id is required"}, None

        slide = self.session.go_to_slide(slide_id)
        if slide:
            return {
                "success": True,
                "navigated_to": slide_id,
                "title": slide.title,
                "reason": reason,
                "narration_hint": slide.narration[:200] + "...",
            }, slide
        else:
            return {
                "success": False,
                "error": f"Invalid slide_id: {slide_id}",
            }, None

    def _handle_get_info(self) -> tuple[dict[str, Any], None]:
        """Handle get_current_slide_info function call."""
        return self.session.get_slide_info(), None

    def _handle_end_presentation(
        self, args: dict[str, Any]
    ) -> tuple[dict[str, Any], None]:
        farewell = args.get("farewell_message", "Thank you for attending!")
        logger.info(f"Ending presentation: {farewell}")
        self.session.is_presenting = False
        return {
            "success": True,
            "action": "end_presentation",
            "farewell": farewell,
        }, None
