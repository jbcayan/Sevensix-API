import enum
import uuid
import logging
import os
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship

from app.chat.utils.private_chat import private_vector_store
from app.chat.utils.public_chat import public_vector_store
from app.config.database import Base
from app.config.settings import settings
from app.config import settings as app_settings

BASE_DIR = app_settings.BASE_DIR

logger = logging.getLogger(__name__)

class InfoType(enum.Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True,
                 nullable=False, default=lambda: str(uuid.uuid4())
                 )
    filename = Column(String(256), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_uid = Column(String, ForeignKey("users.uid"), nullable=True)
    user = relationship("User", back_populates="files")
    status = Column(String(20), default="Not Processed")
    information_type = Column(SqlEnum(InfoType), default=InfoType.PUBLIC)

    def __repr__(self):
        return f"{self.filename} ({self.information_type.value})"

    def get_upload_path(self) -> str:
        return os.path.join(BASE_DIR, "uploads", self.filename)

    def delete_embeddings(self) -> bool:
        try:
            store = private_vector_store if self.information_type == InfoType.PRIVATE else public_vector_store
            col = store._collection
            results = col.get(where={"source": self.filename})
            vector_ids = results.get("ids", [])
            if vector_ids:
                store.delete(ids=vector_ids)
            return True
        except Exception as e:
            logger.exception(f"Error deleting embeddings for {self.filename}")
            return False

    def delete_from_filesystem(self) -> bool:
        try:
            file_path = self.get_upload_path()
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            logger.exception(f"Error deleting file: {self.filename}")
            return False

    def delete(self, db_session):
        """Custom delete to ensure embeddings and file are removed before DB deletion."""
        self.delete_embeddings()
        self.delete_from_filesystem()
        db_session.delete(self)
        db_session.commit()

    async def async_delete(self, db_session):
        """Async version of delete to ensure embeddings and file are removed before DB deletion."""
        self.delete_embeddings()
        self.delete_from_filesystem()
        await db_session.delete(self)
        await db_session.commit()
