from httpx import AsyncClient
from fastapi import status


async def test_response_when_shortcode_is_invalid(client: AsyncClient):
    response = client.post("/shorten", json={"shortcode": "test", "url": "https://www.test.com"})
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert response.json() == {"message": "The provided shortcode is invalid"}

async def test_response_when_url_is_not_present(client: AsyncClient):
    response = client.post("/shorten", json={"shortcode": "test"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": "Url not present"}

async def test_response_when_provided_url_is_invalid(client: AsyncClient):
    response = client.post("/shorten", json={"shortcode": "test", "url": "htts://www.test.com"})
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert response.json() == {"message": "The rpovided url is invalid"}