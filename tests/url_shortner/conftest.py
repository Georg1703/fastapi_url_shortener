import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.url_shortner.comtrollers import generate_alphanum_code

from src.main import app
from src.database import Base
from src.url_shortner.models import Link
from src.database import async_engine


async_session = async_sessionmaker(async_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db_setup_sessionmaker():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture()
async def session(test_db_setup_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

        # delete all data from all tables after test
        for name, table in Base.metadata.tables.items():
            await session.execute(delete(table))
        await session.commit()


@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://localhost/") as client:
        client.headers.update({"Host": "localhost"})
        yield client


@pytest_asyncio.fixture()
async def populate_link_table(session):
    objects = []
    for i in range(1000):
        objects.append(
            Link(
                original_url=f"https://www.test.com/{i}", 
                shortcode=generate_alphanum_code(), 
                last_redirected_at=datetime.now(timezone.utc)
            )
        )
    session.add_all(objects)
    await session.commit()

    