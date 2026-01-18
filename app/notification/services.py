import json
import math
from typing import List, Tuple

from fastapi import Response

from base.enums import Error
from base.exceptions import NotFoundError
from base.settings import redis
from notification.schemas import (
    CreateNotificationSchema,
    GetNotificationsSchema,
    PageMeta,
)
from notification.services_db import create_notification as create_notification_db
from notification.services_db import delete_notification as delete_notification_db
from notification.services_db import fetch_notifications, get_notification_by_user
from user.models import User
from user.schemas import NotificationInstanceSchema, UserMetaSchema


class NotificationService:
    _create_notification = staticmethod(create_notification_db)
    _delete_notification = staticmethod(delete_notification_db)
    _fetch_notifications = staticmethod(fetch_notifications)
    _get_notification_by_user = staticmethod(get_notification_by_user)

    @staticmethod
    async def _notifications_cache_version(uid: int) -> int:
        version = await redis.get(f"notifications:ver:{uid}")
        if version is None:
            return 0
        try:
            return int(version)
        except (TypeError, ValueError):
            return 0

    @classmethod
    async def _notifications_cache_key(cls, uid: int, offset: int, limit: int) -> str:
        version = await cls._notifications_cache_version(uid)
        return f"notifications:{uid}:{version}:{offset}:{limit}"

    @staticmethod
    async def _bump_notifications_cache(uid: int) -> None:
        await redis.incr(f"notifications:ver:{uid}")

    @classmethod
    async def get_notifications(
        cls,
        uid: int,
        params: GetNotificationsSchema,
    ) -> Tuple[List[NotificationInstanceSchema], PageMeta]:
        offset = params.offset
        limit = params.limit

        redis_key = await cls._notifications_cache_key(uid, offset, limit)
        data = await redis.get(redis_key)
        if data:
            payload = json.loads(data)
            cached = [
                NotificationInstanceSchema.model_validate(item)
                for item in payload["data"]
            ]
            meta = PageMeta.model_validate(payload["meta"])
            return cached, meta
        rows, total_items = await cls._fetch_notifications(uid, offset, limit)
        total_pages = math.ceil(total_items / limit) if total_items else 0
        meta = PageMeta(
            offset=offset,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=offset + limit < total_items,
            has_prev=offset > 0,
        )
        result = [
            NotificationInstanceSchema(
                id=i["id"],
                type=i["type"].value,
                text=i.get("text"),
                created_at=i["created_at"],
                user=UserMetaSchema(
                    username=i["user__username"],
                    avatar_url=i.get("user__avatar_url"),
                ),
            )
            for i in rows
        ]
        payload = {
            "data": [item.model_dump(mode="json") for item in result],
            "meta": meta.model_dump(),
        }
        await redis.set(redis_key, json.dumps(payload), ex=60 * 60)
        return result, meta

    @classmethod
    async def delete_notification(cls, uid: int, notification_id: int) -> Response:
        notification = await cls._get_notification_by_user(uid, notification_id)
        if not notification:
            raise NotFoundError(
                code="notification_not_found",
                message=Error.NOT_FOUND.value,
            )
        await cls._delete_notification(notification)
        await cls._bump_notifications_cache(uid)
        return Response(status_code=204)

    @classmethod
    async def create_notification(
        cls, user: User, body: CreateNotificationSchema
    ) -> None:
        await cls._create_notification(user, body.type, body.text)
        await cls._bump_notifications_cache(user.id)
