from datetime import datetime
from mongoengine import (
    DynamicDocument, FileField, DateTimeField, StringField
)


class TimeStampedModel:
    create_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class FileInfo(DynamicDocument, TimeStampedModel):
    file = FileField()
    file_type = StringField()
