from types import SimpleNamespace

import pytest

from base.exceptions import AppException
from user.schemas import CreateUserSchemaSchema
from user.services import UserService


@pytest.mark.asyncio
async def test_register_user_rejects_existing(monkeypatch):
    async def fake_exists(username: str) -> bool:
        return True

    monkeypatch.setattr(UserService, "_user_exists", fake_exists)
    body = CreateUserSchemaSchema.model_validate(
        {
            "username": "user_123",
            "password": "StrongPass1!",
            "avatar_url": None,
        }
    )

    with pytest.raises(AppException) as exc:
        await UserService.register_user(body)

    assert exc.value.status_code == 409


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

    monkeypatch.setattr(UserService, "_user_exists", fake_exists)
    monkeypatch.setattr(UserService, "_create_user", fake_create_user_db)

    body = CreateUserSchemaSchema.model_validate(
        {
            "username": "user_456",
            "password": "StrongPass1!",
            "avatar_url": None,
        }
    )
    user = await UserService.register_user(body)

    assert user.username == body.username
    assert captured["password"] != body.password
