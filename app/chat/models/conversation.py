import enum
import uuid
from sqlalchemy import Column, Integer, String, Text, Enum as SqlEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class ConversationType(enum.Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True,
                 nullable=False, default=lambda: str(uuid.uuid4())
                 )
    user_uid = Column(String, ForeignKey("users.uid", ondelete="SET NULL"), nullable=True)
    user = relationship("User", back_populates="conversations")

    conversation_type = Column(SqlEnum(ConversationType), default=ConversationType.PUBLIC)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)

    def __repr__(self):
        return f"Conversation {self.id} ({self.conversation_type.value})"
