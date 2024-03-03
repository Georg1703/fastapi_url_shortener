from contextlib import ExitStack

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient

from src.database import get_db, sessionmanager
from src.main import app
from src.config import settings

@pytest.fixture(autouse=True)
def get_app():
    sessionmanager.init(settings.DATABASE_URL)
    with ExitStack():
        yield app


@pytest.fixture
def client(get_app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def transactional_session():
    async with sessionmanager.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction


@pytest.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(get_app, db_session):
    async def get_db_session_override():
        yield db_session

    get_app.dependency_overrides[get_db] = get_db_session_override