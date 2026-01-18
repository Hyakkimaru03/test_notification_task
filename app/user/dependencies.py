from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from base.exceptions import UnauthorizedError
from user.services import UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise UnauthorizedError(code="auth_required", message="Authorization required")
    uid = UserService.get_uid_or_raise(request)
    user = await UserService.get_user_by_id(uid)
    if not user:
        raise UnauthorizedError(code="auth_invalid", message="Invalid user")
    return user


async def get_uid(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise UnauthorizedError(code="auth_required", message="Authorization required")
    return UserService.get_uid_or_raise(request)
