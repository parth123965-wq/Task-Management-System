from fastapi import Depends, APIRouter, Request, Response
from app.service.user_service import UserService
from app.dependancys.user_depend import get_current_user
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.dependancys.user_depend import get_user_service
from app.core.config import setting
from app.model.user_model import User

user_router = APIRouter(prefix="/users",tags=["Users"])

@user_router.post('/register',response_model=UserResponse)
async def register(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
)->UserResponse:
    result = await service.register_user(data=user)
    return result

@user_router.get('/me',response_model=UserResponse)
async def me(
    request: Request,
    user: User = Depends(get_current_user)
)->UserResponse:
    return user

@user_router.post('/login')
async def login(
    user: UserLogin,
    response: Response,
    service: UserService = Depends(get_user_service)
):  
    access_token, refresh_token = await service.login_user(user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=20*60,
        **setting.COOKIE_SETTING
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=60*60,
        **setting.COOKIE_SETTING
    )
    return {"message":"Login successful"}

@user_router.post('/logout')
async def logout(
    response: Response,
    user: User = Depends(get_current_user)
):
    response.delete_cookie(
        key="access_token",
        httponly=setting.COOKIE_HTTPONLY,
        samesite=setting.COOKIE_SAMESITE,
        secure=setting.COOKIE_SECURE,
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=setting.COOKIE_HTTPONLY,
        samesite=setting.COOKIE_SAMESITE,
        secure=setting.COOKIE_SECURE,
    )

    return {"message": "Logged out successfully"}