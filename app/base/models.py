from tortoise import Model, fields


class BaseModel(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True
