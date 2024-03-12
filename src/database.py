from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings

Base = declarative_base()


if settings.ENVIRONMENT == "PYTEST":
    sqlalchemy_database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
else:
    sqlalchemy_database_uri = settings.DEFAULT_SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
session_maker = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncGenerator:
    async with session_maker() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)