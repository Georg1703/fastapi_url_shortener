from datetime import datetime

from httpx import AsyncClient
from fastapi import status
import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.url_shortner.models import Link


@pytest.mark.asyncio
async def test_response_when_shortcode_is_invalid(client: AsyncClient):
    response = await client.post("/shorten", json={"shortcode": "test", "url": "https://www.test.com"})
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert response.json() == {"message": "The provided shortcode is invalid"}


@pytest.mark.asyncio
async def test_response_when_url_is_not_present(client: AsyncClient):
    response = await client.post("/shorten", json={"shortcode": "test"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": "Url not present"}


@pytest.mark.asyncio
async def test_response_when_provided_url_is_invalid(client: AsyncClient):
    response = await client.post("/shorten", json={"shortcode": "test", "url": "htts://www.test.com"})
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert response.json() == {"message": "The rpovided url is invalid"}


@pytest.mark.asyncio
async def test_link_creation_without_shortcode(session: AsyncSession, client: AsyncClient):
    """Test that the link is created in the database without shortcode provided"""

    response = await client.post("/shorten", json={"url": "https://www.test.com/1"})

    objects_count = await session.execute(select(func.count()).select_from(Link))
    obj = await session.execute(select(Link))
    assert response.status_code == status.HTTP_201_CREATED
    assert objects_count.scalar() == 1
    assert obj.scalar().shortcode == response.json()["shortcode"]


@pytest.mark.asyncio
async def test_link_creation(session: AsyncSession, client: AsyncClient):
    """Test that the link is created in the database"""

    response = await client.post("/shorten", json={"shortcode": "test12", "url": "https://www.test.com/1"})

    objects_count = await session.execute(select(func.count()).select_from(Link))
    obj = await session.execute(select(Link))
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["shortcode"] == "test12"
    assert objects_count.scalar() == 1
    assert obj.scalar().shortcode == "test12"


@pytest.mark.asyncio
async def test_link_request_with_same_url(session: AsyncSession, client: AsyncClient):
    """
    Test that the link is not created in the database if the url 
    already exists and existing shortcode is returned
    """

    objects_count = await session.execute(select(func.count()).select_from(Link))
    assert objects_count.scalar() == 0
    await client.post("/shorten", json={"shortcode": "test12", "url": "https://www.test.com/1"})
    response = await client.post("/shorten", json={"shortcode": "fake12", "url": "https://www.test.com/1"})

    objects_count = await session.execute(select(func.count()).select_from(Link))
    obj = await session.execute(select(Link))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["shortcode"] == "test12"
    assert objects_count.scalar() == 1
    assert obj.scalar().shortcode == "test12"


@pytest.mark.asyncio
async def test_link_request_with_same_shortcode(session: AsyncSession, client: AsyncClient):
    """
    Test that correct status code and content is returned 
    if shortcode is already in use
    """

    await client.post("/shorten", json={"shortcode": "test12", "url": "https://www.test.com/1"})
    response = await client.post("/shorten", json={"shortcode": "test12", "url": "https://www.another_test.com/1"})

    objects_count = await session.execute(select(func.count()).select_from(Link))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Shortcode already in use"}
    assert objects_count.scalar() == 1


@pytest.mark.asyncio
async def test_get_original_url_by_shortcode(session: AsyncSession, client: AsyncClient):
    """
    Test that correct status code is returned and correct url is included 
    in headers for provided shortcode
    """

    request_data = {"shortcode": "test12", "url": "https://www.test.com/1"}
    response = await client.post("/shorten", json=request_data)
    shortcode = response.json()["shortcode"]
    response = await client.get(f"/{shortcode}")

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["Location"] == request_data["url"]


@pytest.mark.asyncio
async def test_shortcode_not_found(session: AsyncSession, client: AsyncClient):
    """Test that 404 code is returned if shortcode was not found"""

    response = await client.get("/fake12")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Location" not in response.headers


@pytest.mark.asyncio
async def test_get_shortcode_statistic(session: AsyncSession, client: AsyncClient):
    request_data = {"shortcode": "test12", "url": "https://www.test.com/1"}
    response = await client.post("/shorten", json=request_data)
    shortcode = response.json()["shortcode"]

    response = await client.get(f"/{shortcode}/stats")

    assert response.json()['redirect_count'] == 0

    await client.get(f"/{shortcode}")
    response = await client.get(f"/{shortcode}/stats")

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert datetime.fromisoformat(data["last_redirected"])
    assert datetime.fromisoformat(data["created"])
    assert data['redirect_count'] == 1


@pytest.mark.asyncio
async def test_shortcode_stats_not_found(session: AsyncSession, client: AsyncClient):
    """Test that 404 code is returned if shortcode was not found"""

    response = await client.get("/fake12/stats")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Location" not in response.headers