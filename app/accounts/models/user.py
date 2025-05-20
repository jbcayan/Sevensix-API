from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, String, Integer
from sqlalchemy.orm import relationship
from app.config.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    PUBLIC = "public"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True,
                 nullable=False, default=lambda: str(uuid.uuid4())
                 )
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        Enum(RoleEnum, name="user_role", native_enum=False),
        default=RoleEnum.MODERATOR,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    files = relationship("File", back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User(username={self.username!r}, role={self.role.value})>"