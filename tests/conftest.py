import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from faker import Faker

from backend.app.main import app
from backend.app.database import AsyncSessionLocal
from backend.app.models import Base
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
def test_db_engine():
    """Create test database engine using SQLite for faster tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )
    return engine

@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def override_get_db(test_db_session: AsyncSession):
    """Override database dependency for testing."""
    async def _override_get_db():
        yield test_db_session
    
    return _override_get_db

@pytest.fixture
def client() -> Generator:
    """Create test client for FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def async_client() -> AsyncClient:
    """Create async test client for FastAPI app."""
    return AsyncClient(app=app, base_url="http://test")

@pytest.fixture
def mock_celery():
    """Mock Celery app and tasks."""
    with patch('backend.app.main.celery_app') as mock_celery_app:
        with patch('backend.app.main.process_log_task') as mock_task:
            mock_result = Mock()
            mock_result.id = "test-task-id-123"
            mock_task.delay.return_value = mock_result
            yield mock_celery_app, mock_task

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
def mock_async_session():
    """Mock async database session."""
    with patch('backend.app.database.AsyncSessionLocal') as mock_session:
        mock_session.return_value.__aenter__.return_value = Mock()
        yield mock_session

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
