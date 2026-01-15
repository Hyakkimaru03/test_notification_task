from fastapi import APIRouter, Depends

from notification.schemas import CreateNotificationSchema, GetNotificationsSchema, Page
from services import create_notification as create_notification_service
from services import delete_notification as delete_notification_service
from services import get_notifications as get_notifications_service
from user.dependencies import get_uid, get_user
from user.models import User
from user.schemas import NotificationInstanceSchema

notification_router = APIRouter()


@notification_router.get("/", response_model=Page[NotificationInstanceSchema])
async def get_notifications(
    uid: int = Depends(get_uid), params: GetNotificationsSchema = Depends()
):
    data, meta = await get_notifications_service(uid, params)
    return Page(data=data, meta=meta)


@notification_router.delete("/{notification_id}")
async def delete_notification(notification_id: int, uid: int = Depends(get_uid)):
    return await delete_notification_service(uid, notification_id)


@notification_router.post("/create")
async def create_notification(
    body: CreateNotificationSchema, user: User = Depends(get_user)
):
    await create_notification_service(user, body)
