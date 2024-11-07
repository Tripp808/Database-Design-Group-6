import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from api.main import app

@pytest.mark.asyncio
async def test_create_customer():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/customers/", json={
            "name": "test",
            "email": "test@test.com",
            "address": "test address"
        })
    assert response.status_code == 200
    assert "customer_id" in response.json()
