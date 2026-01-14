from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Optional

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise.contrib.fastapi import register_tortoise

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import services
from notification.router import notification_router
from user.router import auth_router


class FakeRedis:
    def __init__(self) -> None:
        self._store: Dict[str, object] = {}

    async def get(self, key: str):
        return self._store.get(key)

    async def set(self, key: str, value, ex: Optional[int] = None):
        self._store[key] = value

    async def incr(self, key: str) -> int:
        value = self._store.get(key, 0)
        try:
            current = int(value)
        except (TypeError, ValueError):
            current = 0
        current += 1
        self._store[key] = current
        return current


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(services, "redis", fake)
    return fake


@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch):
    monkeypatch.setattr(services, "JWT_SECRET", "test-secret")


@pytest.fixture(scope="session")
def db_url(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db")
    db_file = db_dir / "test.sqlite3"
    return f"sqlite://{db_file.as_posix()}"


@pytest.fixture()
def app(db_url):
    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        await app_instance.router.startup()
        try:
            yield
        finally:
            await app_instance.router.shutdown()

    app = FastAPI(lifespan=lifespan)
    app.include_router(
        notification_router, prefix="/notifications", tags=["notifications"]
    )
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    register_tortoise(
        app,
        config={
            "connections": {"default": db_url},
            "apps": {
                "models": {
                    "models": ["user.models", "notification.models"],
                    "default_connection": "default",
                }
            },
            "timezone": "UTC",
            "use_tz": True,
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )
    return app


@pytest.fixture()
async def client(app):
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
