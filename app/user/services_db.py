from typing import Optional

from user.models import User


async def user_exists(username: str) -> bool:
    return await User.exists(username=username)


async def create_user(username: str, password: str, avatar_url: Optional[str]) -> User:
    return await User.create(
        username=username, password=password, avatar_url=avatar_url
    )


async def get_user_by_username(username: str) -> Optional[User]:
    return await User.get_or_none(username=username)


async def get_user_by_id(uid: int) -> Optional[User]:
    return await User.get_or_none(id=uid)
