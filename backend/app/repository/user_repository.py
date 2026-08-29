from app.model.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, or_, Sequence
from typing import Dict, Any, Optional
import uuid
from datetime import datetime,timezone

class UserRepository:
    def __init__(self, sesion: AsyncSession):
        self.session = sesion
        
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh()
        return user
    
    async def update(self, db_user: User, data: Dict[str,Any])->User:
        for field, value in data.items():
            setattr(db_user,field,value)
        await self.session.flush()
        await self.session.refresh()
        return db_user
    
    async def soft_delete(self, user_id: uuid.UUID) -> bool:
        statement = (
            update(User)
            .where(User.id==user_id,User.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc),is_active=False)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None
    
    async def get_by_id(self, user_id: uuid.UUID)->Optional[User]:
        statement = select(User).where(
            User.id==user_id,User.deleted_at.is_(None)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str)->Optional[User]:
        statement = select(User).where(User.username==username,User.deleted_at.is_(None))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str)->Optional[User]:
        statement = select(User).where(User.email==email,User.deleted_at.is_(None))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_identifier(self, identifier: str)->Optional[User]:
        statement = select(User).where(or_(User.email==identifier,User.username==identifier),User.deleted_at.is_(None))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_multi(self, limit: int = 50, skip: int = 0)->Sequence[User]:
        statement = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()