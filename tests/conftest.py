import pytest
import pytest_asyncio
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch
from datetime import datetime, timedelta
from faker import Faker
from unittest.mock import patch

from backend.app.main import app
from backend.app.schemas import LogCreate

# Create Faker instance for test data
fake = Faker()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator:
    """Create test client for FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_log_data():
    """Sample log data for testing."""
    return {
        "service": "test-service",
        "level": "ERROR",
        "message": "Test error message",
        "timestamp": datetime.now(),
        "metadata": {"user_id": 123, "request_id": "req-456"}
    }

@pytest.fixture
def sample_log_create():
    """Sample LogCreate instance for testing."""
    return LogCreate(
        service="test-service",
        level="ERROR",
        message="Test error message",
        timestamp=datetime.now(),
        metadata={"user_id": 123, "request_id": "req-456"}
    )

@pytest.fixture
def multiple_logs_data():
    """Multiple log entries for testing."""
    base_time = datetime.now()
    return [
        {
            "service": "service-a",
            "level": "ERROR",
            "message": "Error in service A",
            "timestamp": base_time - timedelta(minutes=5),
            "metadata": {"error_code": "E001"}
        },
        {
            "service": "service-a",
            "level": "WARN",
            "message": "Warning in service A",
            "timestamp": base_time - timedelta(minutes=4),
            "metadata": {"warning_code": "W001"}
        },
        {
            "service": "service-b",
            "level": "ERROR",
            "message": "Error in service B",
            "timestamp": base_time - timedelta(minutes=3),
            "metadata": {"error_code": "E002"}
        },
        {
            "service": "service-b",
            "level": "INFO",
            "message": "Info in service B",
            "timestamp": base_time - timedelta(minutes=2),
            "metadata": {"info_code": "I001"}
        }
    ]


@pytest.fixture
def fixed_datetime():
    """Fixed datetime for consistent testing."""
    return datetime(2024, 1, 15, 12, 0, 0)

@pytest.fixture
def mock_async_result():
    """Mock AsyncResult for Celery tasks."""
    with patch('backend.app.main.AsyncResult') as mock_result:
        mock_result.return_value.status = "SUCCESS"
        mock_result.return_value.result = {"processed": True}
        yield mock_result
