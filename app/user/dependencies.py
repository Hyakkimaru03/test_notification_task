from fastapi import HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED

from services import get_uid_or_raise
from services_db import get_user_by_id


async def get_user(request: Request):
    uid = get_uid_or_raise(request)
    user = await get_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return user


async def get_uid(request: Request):
    return get_uid_or_raise(request)
