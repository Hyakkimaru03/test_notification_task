from uuid import uuid4

import pytest
from httpx import AsyncClient

from user.schemas import AccessTokenResponse, RegisterResponse, TokenPair


@pytest.mark.asyncio
async def test_register_login_refresh(client: AsyncClient):
    username = f"user_{uuid4().hex[:8]}"
    password = "StrongPass1!"

    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "avatar_url": None,
        },
    )
    assert response.status_code == 200
    RegisterResponse.model_validate(response.json())

    response = await client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200
    tokens = TokenPair.model_validate(response.json())

    response = await client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {tokens.refresh_token}"},
    )
    assert response.status_code == 200
    AccessTokenResponse.model_validate(response.json())
