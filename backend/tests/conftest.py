import pytest
from httpx import AsyncClient
from app.main import app
from app.database import AsyncSessionLocal, engine
from app.models import Base
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    # Cria tabelas temporárias no banco de teste
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
