import pytest
from fastapi.testclient import TestClient

from app.data.slides import SLIDES


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_healthy(self, client: TestClient) -> None:
        """Health endpoint should return healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_check_is_fast(self, client: TestClient) -> None:
        """Health endpoint should respond quickly (< 100ms)."""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # Should be under 100ms


class TestSlidesListEndpoint:
    """Tests for GET /api/slides endpoint."""

    def test_get_all_slides_returns_list(self, client: TestClient) -> None:
        """Should return all slides as a list."""
        response = client.get("/api/slides")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(SLIDES)

    def test_get_all_slides_has_correct_structure(self, client: TestClient) -> None:
        """Each slide should have required fields."""
        response = client.get("/api/slides")
        data = response.json()

        required_fields = {"id", "title", "content", "narration", "iconName"}
        for slide in data:
            assert required_fields.issubset(slide.keys())

    def test_slides_are_ordered_by_id(self, client: TestClient) -> None:
        """Slides should be returned in order by ID."""
        response = client.get("/api/slides")
        data = response.json()

        ids = [slide["id"] for slide in data]
        assert ids == sorted(ids)
        assert ids == list(range(1, len(data) + 1))

    def test_slides_have_content(self, client: TestClient) -> None:
        """Each slide should have non-empty content."""
        response = client.get("/api/slides")
        data = response.json()

        for slide in data:
            assert len(slide["title"]) > 0
            assert len(slide["content"]) > 0
            assert len(slide["narration"]) > 0

    def test_content_is_list_of_strings(self, client: TestClient) -> None:
        """Slide content should be a list of strings."""
        response = client.get("/api/slides")
        data = response.json()

        for slide in data:
            assert isinstance(slide["content"], list)
            for item in slide["content"]:
                assert isinstance(item, str)
                assert len(item) > 0


class TestSlideByIdEndpoint:
    """Tests for GET /api/slides/{slide_id} endpoint."""

    def test_get_first_slide(self, client: TestClient) -> None:
        """Should return the first slide."""
        response = client.get("/api/slides/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "title" in data

    def test_get_last_slide(self, client: TestClient) -> None:
        """Should return the last slide."""
        last_id = len(SLIDES)
        response = client.get(f"/api/slides/{last_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == last_id

    def test_get_middle_slide(self, client: TestClient) -> None:
        """Should return a middle slide."""
        middle_id = len(SLIDES) // 2 + 1
        response = client.get(f"/api/slides/{middle_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == middle_id

    def test_get_slide_returns_correct_structure(self, client: TestClient) -> None:
        """Returned slide should have all required fields."""
        response = client.get("/api/slides/1")
        data = response.json()

        required_fields = {"id", "title", "content", "narration", "iconName"}
        assert required_fields.issubset(data.keys())

    # Edge Cases

    def test_get_slide_invalid_id_zero(self, client: TestClient) -> None:
        """Should return 404 for slide ID 0."""
        response = client.get("/api/slides/0")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_slide_invalid_id_negative(self, client: TestClient) -> None:
        """Should return 404 for negative slide ID."""
        response = client.get("/api/slides/-1")

        assert response.status_code == 404

    def test_get_slide_invalid_id_too_high(self, client: TestClient) -> None:
        """Should return 404 for slide ID beyond total."""
        invalid_id = len(SLIDES) + 1
        response = client.get(f"/api/slides/{invalid_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_slide_invalid_id_very_large(self, client: TestClient) -> None:
        """Should return 404 for very large slide ID."""
        response = client.get("/api/slides/99999")

        assert response.status_code == 404

    def test_get_slide_invalid_id_string(self, client: TestClient) -> None:
        """Should return 422 for non-integer slide ID."""
        response = client.get("/api/slides/abc")

        assert response.status_code == 422  # Validation error

    def test_get_slide_invalid_id_float(self, client: TestClient) -> None:
        """Should return 422 for float slide ID."""
        response = client.get("/api/slides/1.5")

        assert response.status_code == 422


class TestAPIEdgeCases:
    """Additional edge case tests for API."""

    def test_nonexistent_endpoint(self, client: TestClient) -> None:
        """Should return 404 for nonexistent endpoint."""
        response = client.get("/api/nonexistent")

        assert response.status_code == 404

    def test_wrong_method_on_slides(self, client: TestClient) -> None:
        """Should return 405 for wrong HTTP method."""
        response = client.post("/api/slides")

        assert response.status_code == 405

    def test_wrong_method_on_health(self, client: TestClient) -> None:
        """Should return 405 for POST on health endpoint."""
        response = client.post("/health")

        assert response.status_code == 405

    def test_slides_response_is_json(self, client: TestClient) -> None:
        """Response should be valid JSON with correct content type."""
        response = client.get("/api/slides")

        assert response.headers["content-type"] == "application/json"
        # Should not raise
        response.json()

    def test_concurrent_requests(self, client: TestClient) -> None:
        """API should handle multiple requests correctly."""
        import concurrent.futures

        def make_request() -> int:
            return client.get("/api/slides").status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]

        assert all(status == 200 for status in results)
