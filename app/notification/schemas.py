from typing import Generic, List, Optional, TypeVar

from fastapi.params import Query
from pydantic import BaseModel

from base.enums import NotificationType

T = TypeVar("T")
MAX_LIMIT = 100


class BasePaginationSchema(BaseModel):
    offset: int = Query(ge=0, default=0)
    limit: int = Query(ge=1, le=MAX_LIMIT, default=20)


class PageMeta(BaseModel):
    offset: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class Page(BaseModel, Generic[T]):
    data: List[T]
    meta: PageMeta


class GetNotificationsSchema(BasePaginationSchema):
    pass


class CreateNotificationSchema(BaseModel):
    type: NotificationType
    text: Optional[str] = None
