from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from base.enums import NotificationType


class UserMetaSchema(BaseModel):
    username: str = Field(..., max_length=32, min_length=3)
    avatar_url: Optional[str] = None


class NotificationInstanceSchema(BaseModel):
    id: int
    type: NotificationType
    text: Optional[str] = None
    created_at: datetime
    user: UserMetaSchema


class CreateUserSchemaSchema(BaseModel):
    username: str = Field(..., max_length=32, min_length=3)
    avatar_url: Optional[str] = None
    password: str = Field(..., max_length=32, min_length=8)


class LoginUserSchema(BaseModel):
    username: str = Field(..., max_length=32, min_length=3)
    password: str = Field(..., max_length=32, min_length=8)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RegisterResponse(BaseModel):
    user_id: int
    tokens: TokenPair


class AccessTokenResponse(BaseModel):
    access_token: str
