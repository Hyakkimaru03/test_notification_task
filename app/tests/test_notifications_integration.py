from uuid import uuid4

import pytest
from httpx import AsyncClient

from notification.schemas import Page
from user.schemas import NotificationInstanceSchema


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

    response = await client.post(
        "/notifications/create",
        json={
            "type": "Like",
            "text": "Hello",
        },
    )
    assert response.status_code == 200

    response = await client.get("/notifications/", params={"page": 1, "page_size": 20})
    assert response.status_code == 200
    page = Page[NotificationInstanceSchema].model_validate(response.json())
    assert len(page.data) == 1

    notification_id = page.data[0].id
    response = await client.delete(f"/notifications/{notification_id}")
    assert response.status_code == 200

    response = await client.get("/notifications/", params={"page": 1, "page_size": 20})
    assert response.status_code == 200
    page = Page[NotificationInstanceSchema].model_validate(response.json())
    assert page.data == []
