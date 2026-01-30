import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.data.slides import SLIDES


class TestWebSocketConnection:
    """Tests for WebSocket connection handling."""

    def test_websocket_connects(self, client: TestClient) -> None:
        """WebSocket should accept connections."""
        with client.websocket_connect("/ws") as websocket:
            # Connection established
            # Should receive initial slide.changed event
            data = websocket.receive_json()
            assert data["type"] == "slide.changed"

    def test_websocket_initial_slide_event(self, client: TestClient) -> None:
        """WebSocket should send initial slide on connect."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "slide.changed"
            assert data["slide_id"] == 1
            assert "title" in data
            assert "content" in data
            assert data["total_slides"] == len(SLIDES)
            assert data["has_previous"] is False
            assert data["has_next"] is True

    def test_websocket_closes_cleanly(self, client: TestClient) -> None:
        """WebSocket should close without errors."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Consume initial event
            # Context manager handles close
        # No exception means clean close


class TestWebSocketSlideNavigation:
    """Tests for slide navigation via WebSocket."""

    def test_navigate_next(self, client: TestClient) -> None:
        """Should navigate to next slide."""
        with client.websocket_connect("/ws") as websocket:
            # Consume initial event
            websocket.receive_json()

            # Send navigate next
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()

            assert data["type"] == "slide.changed"
            assert data["slide_id"] == 2

    def test_navigate_prev(self, client: TestClient) -> None:
        """Should navigate to previous slide."""
        with client.websocket_connect("/ws") as websocket:
            # Go to slide 3 first
            websocket.receive_json()
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            websocket.receive_json()
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            websocket.receive_json()

            # Now go prev
            websocket.send_json({"type": "slide.navigate", "direction": "prev"})
            data = websocket.receive_json()

            assert data["slide_id"] == 2

    def test_navigate_prev_on_first_slide(self, client: TestClient) -> None:
        """Should not navigate before first slide."""
        with client.websocket_connect("/ws") as websocket:
            initial = websocket.receive_json()
            assert initial["slide_id"] == 1

            # Try to go prev - should not send new event (stays on slide 1)
            websocket.send_json({"type": "slide.navigate", "direction": "prev"})

            # Send another command to verify we're still on slide 1
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2

    def test_goto_slide(self, client: TestClient) -> None:
        """Should go to specific slide."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "slide.goto", "slide_id": 4})
            data = websocket.receive_json()

            assert data["type"] == "slide.changed"
            assert data["slide_id"] == 4

    def test_goto_first_slide(self, client: TestClient) -> None:
        """Should go to first slide."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Go somewhere else first
            websocket.send_json({"type": "slide.goto", "slide_id": 3})
            websocket.receive_json()

            # Go back to slide 1
            websocket.send_json({"type": "slide.goto", "slide_id": 1})
            data = websocket.receive_json()

            assert data["slide_id"] == 1
            assert data["has_previous"] is False

    def test_goto_last_slide(self, client: TestClient) -> None:
        """Should go to last slide."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            last_id = len(SLIDES)
            websocket.send_json({"type": "slide.goto", "slide_id": last_id})
            data = websocket.receive_json()

            assert data["slide_id"] == last_id
            assert data["has_next"] is False

    def test_goto_invalid_slide(self, client: TestClient) -> None:
        """Should not change slide for invalid ID."""
        with client.websocket_connect("/ws") as websocket:
            initial = websocket.receive_json()

            # Try invalid slide
            websocket.send_json({"type": "slide.goto", "slide_id": 999})

            # Next navigation should start from slide 1
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2


class TestWebSocketSlideChangedEvent:
    """Tests for slide.changed event details."""

    def test_slide_changed_has_content(self, client: TestClient) -> None:
        """slide.changed should include content array."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            assert isinstance(data["content"], list)
            assert len(data["content"]) > 0

    def test_slide_changed_has_narration(self, client: TestClient) -> None:
        """slide.changed should include narration."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            assert "narration" in data
            assert len(data["narration"]) > 0

    def test_slide_changed_navigation_flags(self, client: TestClient) -> None:
        """slide.changed should have correct navigation flags."""
        with client.websocket_connect("/ws") as websocket:
            # First slide
            first = websocket.receive_json()
            assert first["has_previous"] is False
            assert first["has_next"] is True

            # Middle slide
            websocket.send_json({"type": "slide.goto", "slide_id": 3})
            middle = websocket.receive_json()
            assert middle["has_previous"] is True
            assert middle["has_next"] is True

            # Last slide
            websocket.send_json({"type": "slide.goto", "slide_id": len(SLIDES)})
            last = websocket.receive_json()
            assert last["has_previous"] is True
            assert last["has_next"] is False


class TestWebSocketSequence:
    """Tests for sequences of WebSocket operations."""

    def test_full_slide_traversal(self, client: TestClient) -> None:
        """Should traverse all slides forward."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["slide_id"] == 1

            for expected_id in range(2, len(SLIDES) + 1):
                websocket.send_json({"type": "slide.navigate", "direction": "next"})
                data = websocket.receive_json()
                assert data["slide_id"] == expected_id

    def test_back_and_forth_navigation(self, client: TestClient) -> None:
        """Should handle back and forth navigation."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # slide 1

            # Go to slide 3
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            websocket.receive_json()  # slide 2
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()  # slide 3
            assert data["slide_id"] == 3

            # Go back
            websocket.send_json({"type": "slide.navigate", "direction": "prev"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2

            # Go forward
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 3

    def test_mixed_navigation_methods(self, client: TestClient) -> None:
        """Should handle mixed goto and navigate operations."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Use goto
            websocket.send_json({"type": "slide.goto", "slide_id": 4})
            data = websocket.receive_json()
            assert data["slide_id"] == 4

            # Use navigate next
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 5

            # Use navigate prev
            websocket.send_json({"type": "slide.navigate", "direction": "prev"})
            data = websocket.receive_json()
            assert data["slide_id"] == 4

            # Use goto back to start
            websocket.send_json({"type": "slide.goto", "slide_id": 1})
            data = websocket.receive_json()
            assert data["slide_id"] == 1


class TestWebSocketSessionEvents:
    """Tests for session start/stop events."""

    def test_session_stop_event(self, client: TestClient) -> None:
        """Should handle session.stop event."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Initial slide

            # Send stop - should be handled without error
            websocket.send_json({"type": "session.stop"})
            # No response expected, connection should remain open


class TestWebSocketEdgeCases:
    """Edge case tests for WebSocket."""

    def test_unknown_event_type(self, client: TestClient) -> None:
        """Should handle unknown event types gracefully."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send unknown event
            websocket.send_json({"type": "unknown.event"})

            # Should still work for valid events
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2

    def test_malformed_json_event(self, client: TestClient) -> None:
        """Should handle events with missing fields."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send event missing required field
            websocket.send_json({"type": "slide.goto"})  # Missing slide_id

            # Should still work for valid events
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2

    def test_empty_event(self, client: TestClient) -> None:
        """Should handle empty event object."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({})

            # Should still work
            websocket.send_json({"type": "slide.navigate", "direction": "next"})
            data = websocket.receive_json()
            assert data["slide_id"] == 2

    def test_rapid_navigation(self, client: TestClient) -> None:
        """Should handle rapid navigation commands."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send many commands rapidly
            for _ in range(3):
                websocket.send_json({"type": "slide.navigate", "direction": "next"})

            # Collect responses
            responses = []
            for _ in range(3):
                responses.append(websocket.receive_json())

            # Should end up on slide 4
            assert responses[-1]["slide_id"] == 4

    def test_multiple_connections(self, client: TestClient) -> None:
        """Multiple WebSocket connections should be independent."""
        with client.websocket_connect("/ws") as ws1:
            data1 = ws1.receive_json()
            assert data1["slide_id"] == 1

            with client.websocket_connect("/ws") as ws2:
                data2 = ws2.receive_json()
                assert data2["slide_id"] == 1

                # Navigate ws1 to slide 3
                ws1.send_json({"type": "slide.goto", "slide_id": 3})
                ws1.receive_json()

                # ws2 should still be on slide 1
                ws2.send_json({"type": "slide.navigate", "direction": "next"})
                data2 = ws2.receive_json()
                assert data2["slide_id"] == 2  # Moved from 1 to 2, not from 3
