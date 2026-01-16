from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from user.services import UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    uid = UserService.get_uid_or_raise(request)
    user = await UserService.get_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return user


async def get_uid(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return UserService.get_uid_or_raise(request)
