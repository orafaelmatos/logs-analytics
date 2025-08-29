# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

SYNC_DATABASE_URL = os.getenv("POSTGRES_SYNC_URL", "postgresql://postgres:postgres@postgres:5432/logs")
sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(sync_engine, expire_on_commit=False)

# PostgreSQL (analítico)
DATABASE_URL = os.getenv("POSTGRES_URL", f"postgresql+asyncpg://postgres:postgres@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', 5432)}/logs")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# MongoDB (bruto)
MONGO_URL = os.getenv("MONGO_URL", f"mongodb://{os.getenv('MONGO_HOST', 'mongo')}:{os.getenv('MONGO_PORT', 27017)}")
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client.logs
