from uuid import uuid4

import pytest
from httpx import AsyncClient

from notification.schemas import Page
from user.schemas import NotificationInstanceSchema, TokenPair


@pytest.mark.asyncio
async def test_notifications_flow(client: AsyncClient):
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

    response = await client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200
    tokens = TokenPair.model_validate(response.json())
    auth_headers = {"Authorization": f"Bearer {tokens.access_token}"}

    response = await client.post(
        "/notifications/create",
        json={
            "type": "like",
            "text": "Hello",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    response = await client.get(
        "/notifications/", params={"offset": 0, "limit": 20}, headers=auth_headers
    )
    assert response.status_code == 200
    page = Page[NotificationInstanceSchema].model_validate(response.json())
    assert len(page.data) == 1
    assert page.meta.offset == 0
    assert page.meta.limit == 20
    assert page.meta.total_items == 1
    assert page.meta.total_pages == 1
    assert page.meta.has_next is False
    assert page.meta.has_prev is False

    notification_id = page.data[0].id
    response = await client.delete(
        f"/notifications/{notification_id}", headers=auth_headers
    )
    assert response.status_code == 200

    response = await client.get(
        "/notifications/", params={"offset": 0, "limit": 20}, headers=auth_headers
    )
    assert response.status_code == 200
    page = Page[NotificationInstanceSchema].model_validate(response.json())
    assert page.data == []
    assert page.meta.offset == 0
    assert page.meta.limit == 20
    assert page.meta.total_items == 0
    assert page.meta.total_pages == 0
    assert page.meta.has_next is False
