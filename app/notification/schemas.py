from typing import Generic, List, Optional, TypeVar

from fastapi.params import Query
from pydantic import BaseModel

from base.enums import NotificationType

T = TypeVar("T")


class BasePaginationSchema(BaseModel):
    page: int = Query(ge=1, default=1)
    page_size: int = Query(ge=1, default=20)


class Page(BaseModel, Generic[T]):
    data: List[T]
    total_pages: int


class GetNotificationsSchema(BasePaginationSchema):
    pass


class CreateNotificationSchema(BaseModel):
    type: NotificationType
    text: Optional[str] = None
