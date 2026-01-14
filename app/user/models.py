from tortoise import fields

from base.models import BaseModel


class User(BaseModel):
    username: str = fields.CharField(max_length=32, unique=True)
    avatar_url: str = fields.TextField(null=True)
    password: str = fields.CharField(max_length=255)
    blocked: bool = fields.BooleanField(default=False)
