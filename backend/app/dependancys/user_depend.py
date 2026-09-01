from app.core.database import get_db
import uuid
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.user_model import User
from app.repository.user_repository import UserRepository
from app.core.security import decode_token
from app.service.user_service import UserService
from app.service.avaitar_storage_service import AvaitarStorageService
from app.core.redis import get_redis
from app.service.otp_service import OtpService
from redis.asyncio import Redis

def get_avaitar_service(avaitar_service: AvaitarStorageService = Depends(AvaitarStorageService)):
    return avaitar_service

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(sesion=db)

async def get_current_user(request: Request, user_repo: UserRepository = Depends(get_user_repo))->User:
    token: Optional[str] = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not Found"
        )
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive or Deleted User."
        )
    return user

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    avaitar_service: AvaitarStorageService = Depends(get_avaitar_service)
) -> UserService:
    return UserService(user_repo=user_repo,avaitar_storage=avaitar_service)

def get_otp_service(
    redis: Redis = Depends(get_redis)
)-> OtpService:
    return OtpService(redis)