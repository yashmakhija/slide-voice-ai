"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.session_manager import FunctionHandler, PresentationSession


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client for API tests."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Async test client for async tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def session() -> PresentationSession:
    """Fresh presentation session for each test."""
    return PresentationSession()


@pytest.fixture
def function_handler(session: PresentationSession) -> FunctionHandler:
    """Function handler with fresh session."""
    return FunctionHandler(session)
