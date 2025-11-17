import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime, timezone

from app.core.lib.db import Base


class Users(Base):
    __tablename__ = "Users"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String(10), nullable=False)
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSessions(Base):
    __tablename__ = "UserSessions"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, index=True, default=uuid.uuid4)
    userId = Column(UNIQUEIDENTIFIER, ForeignKey("Users.id"))
    accessToken = Column(String, nullable=False)
    refreshToken = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
