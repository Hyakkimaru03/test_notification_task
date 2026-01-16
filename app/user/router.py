from fastapi import APIRouter, Request

from services import create_token_pair, login_user, refresh_access_token, register_user
from user.schemas import (
    AccessTokenResponse,
    CreateUserSchemaSchema,
    LoginUserSchema,
    RegisterResponse,
    TokenPair,
)

auth_router = APIRouter()


@auth_router.post("/register", response_model=RegisterResponse)
async def register(body: CreateUserSchemaSchema):
    user = await register_user(body)
    tokens = create_token_pair(user.id)
    return {"user_id": user.id, "tokens": tokens}


@auth_router.post("/login", response_model=TokenPair)
async def login(body: LoginUserSchema):
    user = await login_user(body)
    tokens = create_token_pair(user.id)
    return tokens


@auth_router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(request: Request):
    new_access_token = await refresh_access_token(request)
    return {"access_token": new_access_token}
