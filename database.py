
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,  POSTGRES_HOST, POSTGRES_PORT

DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_async_engine(DB_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=True)
Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
