
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.chat.models.file import InfoType


class FileBase(BaseModel):
    filename: str
    information_type: InfoType = InfoType.PUBLIC


class FileCreate(FileBase):
    pass


class FileOut(FileBase):
    id: int
    uid: str
    filename: str
    uploaded_at: datetime
    status: str
    information_type: InfoType
    user_uid: Optional[str] = None

    class Config:
        from_attributes = True
