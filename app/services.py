import json
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Literal, Tuple

import bcrypt
import jwt
from fastapi import HTTPException, Request, Response, status
from password_validator import PasswordValidator

from base.enums import Error, ErrorMessages
from base.settings import JWT_SECRET, redis
from notification.schemas import (
    CreateNotificationSchema,
    GetNotificationsSchema,
    PageMeta,
)
from services_db import create_notification as create_notification_db
from services_db import create_user as create_user_db
from services_db import delete_notification as delete_notification_db
from services_db import (
    fetch_notifications,
    get_notification_by_user,
    get_user_by_id,
    get_user_by_username,
    user_exists,
)
from user.models import User
from user.schemas import (
    CreateUserSchemaSchema,
    LoginUserSchema,
    NotificationInstanceSchema,
    UserMetaSchema,
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1
REFRESH_TOKEN_EXPIRE_DAYS = 7
password_schema = PasswordValidator()
password_schema.min(8).has().lowercase().uppercase().digits().symbols()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_jwt_token(
    user_id: int, key: Literal["access_token", "refresh_token"]
) -> str:
    now_ = datetime.now(timezone.utc)
    if key == "access_token":
        expire = now_ + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        type_ = "access"
    else:
        expire = now_ + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        type_ = "refresh"

    payload = {
        "pk": user_id,
        "type": type_,
        "iat": now_,
        "exp": expire,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_token_pair(user_id: int) -> Dict[str, str]:
    return {
        "access_token": create_jwt_token(user_id, "access_token"),
        "refresh_token": create_jwt_token(user_id, "refresh_token"),
    }


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


def _get_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def _decode_and_validate_token(
    token: str, expected_type: Literal["access", "refresh"]
) -> dict | None:
    payload = decode_jwt(token)
    if not payload or payload.get("type") != expected_type:
        return None
    return payload


def get_uid_or_raise(request: Request) -> int:
    token = _get_bearer_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    payload = _decode_and_validate_token(token, "access")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload["pk"]


async def register_user(body: CreateUserSchemaSchema) -> User:
    if await user_exists(body.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages[Error.USER_EXISTS.value],
        )
    if not password_schema.validate(body.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages[Error.PASSWORD_WEAK.value],
        )
    return await create_user_db(
        username=body.username,
        password=_hash_password(body.password),
        avatar_url=body.avatar_url,
    )


async def login_user(body: LoginUserSchema) -> User:
    user = await get_user_by_username(body.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages[Error.USER_NOT_FOUND.value],
        )
    if not _verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages[Error.INVALID_PASSWORD.value],
        )
    return user


async def refresh_access_token(request: Request) -> str:
    refresh_token = _get_bearer_token(request)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    validated_data = _decode_and_validate_token(refresh_token, "refresh")
    if not validated_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = await get_user_by_id(validated_data["pk"])
    if not user or user.blocked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return create_jwt_token(user.id, "access_token")


async def _notifications_cache_version(uid: int) -> int:
    version = await redis.get(f"notifications:ver:{uid}")
    if version is None:
        return 0
    try:
        return int(version)
    except (TypeError, ValueError):
        return 0


async def _notifications_cache_key(uid: int, offset: int, limit: int) -> str:
    version = await _notifications_cache_version(uid)
    return f"notifications:{uid}:{version}:{offset}:{limit}"


async def _bump_notifications_cache(uid: int) -> None:
    await redis.incr(f"notifications:ver:{uid}")


async def get_notifications(
    uid: int,
    params: GetNotificationsSchema,
) -> Tuple[List[NotificationInstanceSchema], PageMeta]:
    offset = params.offset
    limit = params.limit

    redis_key = await _notifications_cache_key(uid, offset, limit)
    data = await redis.get(redis_key)
    if data:
        payload = json.loads(data)
        cached = [
            NotificationInstanceSchema.model_validate(item) for item in payload["data"]
        ]
        meta = PageMeta.model_validate(payload["meta"])
        return cached, meta
    rows, total_items = await fetch_notifications(uid, offset, limit)
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


async def delete_notification(uid: int, notification_id: int) -> Response:
    notification = await get_notification_by_user(uid, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages[Error.NOT_FOUND.value],
        )
    await delete_notification_db(notification)
    await _bump_notifications_cache(uid)
    return Response(status_code=status.HTTP_200_OK)


async def create_notification(user: User, body: CreateNotificationSchema) -> None:
    await create_notification_db(user, body.type, body.text)
    await _bump_notifications_cache(user.id)
