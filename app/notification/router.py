from fastapi import APIRouter, Depends, Response, status

from notification.schemas import CreateNotificationSchema, GetNotificationsSchema, Page
from notification.services import NotificationService
from user.dependencies import get_uid, get_user
from user.models import User
from user.schemas import NotificationInstanceSchema

notification_router = APIRouter()


@notification_router.get("/", response_model=Page[NotificationInstanceSchema])
async def get_notifications(
    uid: int = Depends(get_uid), params: GetNotificationsSchema = Depends()
):
    data, meta = await NotificationService.get_notifications(uid, params)
    return Page(data=data, meta=meta)


@notification_router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(notification_id: int, uid: int = Depends(get_uid)):
    return await NotificationService.delete_notification(uid, notification_id)


@notification_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    body: CreateNotificationSchema, user: User = Depends(get_user)
):
    await NotificationService.create_notification(user, body)
    return Response(status_code=status.HTTP_201_CREATED)
