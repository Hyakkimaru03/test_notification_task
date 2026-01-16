from datetime import datetime, timedelta, timezone
from typing import Dict, Literal

import bcrypt
import jwt
from fastapi import HTTPException, Request, status
from password_validator import PasswordValidator

from base.enums import Error, ErrorMessages
from base.settings import JWT_SECRET
from user.models import User
from user.schemas import CreateUserSchemaSchema, LoginUserSchema
from user.services_db import create_user as create_user_db
from user.services_db import get_user_by_id, get_user_by_username, user_exists

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1
REFRESH_TOKEN_EXPIRE_DAYS = 7
password_schema = PasswordValidator()
password_schema.min(8).has().lowercase().uppercase().digits().symbols()


class UserService:
    _user_exists = staticmethod(user_exists)
    _create_user = staticmethod(create_user_db)
    _get_user_by_username = staticmethod(get_user_by_username)
    _get_user_by_id = staticmethod(get_user_by_id)

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    @classmethod
    def create_jwt_token(
        cls, user_id: int, key: Literal["access_token", "refresh_token"]
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

    @classmethod
    def create_token_pair(cls, user_id: int) -> Dict[str, str]:
        return {
            "access_token": cls.create_jwt_token(user_id, "access_token"),
            "refresh_token": cls.create_jwt_token(user_id, "refresh_token"),
        }

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def _get_bearer_token(request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    @classmethod
    def _decode_and_validate_token(
        cls, token: str, expected_type: Literal["access", "refresh"]
    ) -> dict | None:
        payload = cls.decode_jwt(token)
        if not payload or payload.get("type") != expected_type:
            return None
        return payload

    @classmethod
    def get_uid_or_raise(cls, request: Request) -> int:
        token = cls._get_bearer_token(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        payload = cls._decode_and_validate_token(token, "access")
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return payload["pk"]

    @classmethod
    async def get_user_by_id(cls, uid: int) -> User | None:
        return await cls._get_user_by_id(uid)

    @classmethod
    async def register_user(cls, body: CreateUserSchemaSchema) -> User:
        if await cls._user_exists(body.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages[Error.USER_EXISTS.value],
            )
        if not password_schema.validate(body.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages[Error.PASSWORD_WEAK.value],
            )
        return await cls._create_user(
            username=body.username,
            password=cls._hash_password(body.password),
            avatar_url=body.avatar_url,
        )

    @classmethod
    async def login_user(cls, body: LoginUserSchema) -> User:
        user = await cls._get_user_by_username(body.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages[Error.USER_NOT_FOUND.value],
            )
        if not cls._verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages[Error.INVALID_PASSWORD.value],
            )
        return user

    @classmethod
    async def refresh_access_token(cls, request: Request) -> str:
        refresh_token = cls._get_bearer_token(request)
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        validated_data = cls._decode_and_validate_token(refresh_token, "refresh")
        if not validated_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        user = await cls._get_user_by_id(validated_data["pk"])
        if not user or user.blocked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return cls.create_jwt_token(user.id, "access_token")
