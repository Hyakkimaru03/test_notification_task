from typing import List, Optional, Tuple

from notification.models import Notification
from user.models import User


async def create_notification(user: User, type_, text: Optional[str]) -> Notification:
    return await Notification.create(type=type_, text=text, user=user)


async def get_notification_by_user(
    uid: int, notification_id: int
) -> Optional[Notification]:
    return await Notification.get_or_none(user_id=uid, id=notification_id)


async def delete_notification(notification: Notification) -> None:
    await notification.delete()


async def fetch_notifications(
    uid: int, offset: int, limit: int
) -> Tuple[List[dict], int]:
    qs = Notification.filter(user_id=uid).order_by("-created_at", "-id")
    items = (
        await qs.offset(offset)
        .limit(limit)
        .values(
            "id",
            "type",
            "text",
            "user__username",
            "user__avatar_url",
            "created_at",
        )
    )
    total = await qs.count()
    return items, total
