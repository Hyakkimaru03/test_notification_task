from datetime import datetime, timezone

import pytest

import services
from base.enums import NotificationType
from notification.schemas import GetNotificationsSchema
from user.schemas import NotificationInstanceSchema


@pytest.mark.asyncio
async def test_get_notifications_uses_cache(monkeypatch, fake_redis):
    calls = {"count": 0}

    async def fake_fetch_notifications(uid: int, page: int, page_size: int):
        calls["count"] += 1
        return (
            [
                {
                    "id": 1,
                    "type": NotificationType.LIKE,
                    "text": "Hello",
                    "user__username": "user_1",
                    "user__avatar_url": None,
                    "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
                }
            ],
            1,
        )

    monkeypatch.setattr(services, "fetch_notifications", fake_fetch_notifications)

    params = GetNotificationsSchema(page=1, page_size=20)
    data_first, total_first = await services.get_notifications(1, params)
    data_second, total_second = await services.get_notifications(1, params)

    assert calls["count"] == 1
    assert total_first == 1
    assert total_second == 1
    assert isinstance(data_first[0], NotificationInstanceSchema)
    assert data_first[0].id == data_second[0].id
