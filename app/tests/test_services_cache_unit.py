from datetime import datetime, timezone

import pytest

from base.enums import NotificationType
from notification.schemas import GetNotificationsSchema
from notification.services import NotificationService
from user.schemas import NotificationInstanceSchema


@pytest.mark.asyncio
async def test_get_notifications_uses_cache(monkeypatch, fake_redis):
    calls = {"count": 0}

    async def fake_fetch_notifications(uid: int, offset: int, limit: int):
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

    monkeypatch.setattr(
        NotificationService, "_fetch_notifications", fake_fetch_notifications
    )

    params = GetNotificationsSchema(offset=0, limit=20)
    data_first, meta_first = await NotificationService.get_notifications(1, params)
    data_second, meta_second = await NotificationService.get_notifications(1, params)

    assert calls["count"] == 1
    assert meta_first.total_items == 1
    assert meta_first.total_pages == 1
    assert meta_second.total_items == 1
    assert isinstance(data_first[0], NotificationInstanceSchema)
    assert data_first[0].id == data_second[0].id
