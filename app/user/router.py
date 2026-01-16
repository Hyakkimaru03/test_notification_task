from fastapi import APIRouter, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from user.schemas import (
    AccessTokenResponse,
    CreateUserSchemaSchema,
    LoginUserSchema,
    RegisterResponse,
    TokenPair,
)
from user.services import UserService

auth_router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@auth_router.post("/register", response_model=RegisterResponse)
async def register(body: CreateUserSchemaSchema):
    user = await UserService.register_user(body)
    tokens = UserService.create_token_pair(user.id)
    return {"user_id": user.id, "tokens": tokens}


@auth_router.post("/login", response_model=TokenPair)
async def login(body: LoginUserSchema):
    user = await UserService.login_user(body)
    tokens = UserService.create_token_pair(user.id)
    return tokens


@auth_router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    new_access_token = await UserService.refresh_access_token(request)
    return {"access_token": new_access_token}
