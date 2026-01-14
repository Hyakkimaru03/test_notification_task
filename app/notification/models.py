from tortoise import fields
from tortoise.fields import OnDelete

from base.enums import NotificationType
from base.models import BaseModel


class Notification(BaseModel):
    user = fields.ForeignKeyField(model_name="models.User", on_delete=OnDelete.CASCADE)
    type = fields.CharEnumField(NotificationType, default=NotificationType.LIKE)
    text = fields.TextField(null=True)  # поставил null потому что context не известен
