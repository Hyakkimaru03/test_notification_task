from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import services
from user.schemas import CreateUserSchemaSchema


@pytest.mark.asyncio
async def test_register_user_rejects_existing(monkeypatch):
    async def fake_exists(username: str) -> bool:
        return True

    monkeypatch.setattr(services, "user_exists", fake_exists)
    body = CreateUserSchemaSchema.model_validate(
        {
            "username": "user_123",
            "password": "StrongPass1!",
            "avatar_url": None,
        }
    )

    with pytest.raises(HTTPException) as exc:
        await services.register_user(body)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_register_user_creates(monkeypatch):
    async def fake_exists(username: str) -> bool:
        return False

    captured = {}

    async def fake_create_user_db(username: str, password: str, avatar_url):
        captured["password"] = password
        return SimpleNamespace(
            id=1,
            username=username,
            password=password,
            avatar_url=avatar_url,
        )

    monkeypatch.setattr(services, "user_exists", fake_exists)
    monkeypatch.setattr(services, "create_user_db", fake_create_user_db)

    body = CreateUserSchemaSchema.model_validate(
        {
            "username": "user_456",
            "password": "StrongPass1!",
            "avatar_url": None,
        }
    )
    user = await services.register_user(body)

    assert user.username == body.username
    assert captured["password"] != body.password
