from app.core.database import Base
import uuid
from typing import Optional
from datetime import datetime
import enum
from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LEADER = "leader"
    GENERAL = "general"
    
class User(Base):
    __tablename__ = "users"

    # Primary Key (UUIDv4 or UUIDv7 prevents ID enumeration attacks)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Identity Fields (Indexed for fast lookup)
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )

    # Profile & Media
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(1024), 
        nullable=True
    )

    # Role & Authorization (PostgreSQL ENUM)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", create_type=True),
        default=UserRole.GENERAL,
        nullable=False
    )

    # Account Status Flags
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )

    # Audit Timestamps (PostgreSQL TIMESTAMPTZ)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"