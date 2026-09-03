from fastapi import Depends, APIRouter, Request, Response, UploadFile, BackgroundTasks
from app.service.user_service import UserService
from app.dependancys.user_depend import get_current_user, get_email_service, get_otp_service
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin, UserUpdate, ChangePasswordRequest, ChangeEmail, VerifyRegister
from app.dependancys.user_depend import get_user_service
from app.core.config import setting
from app.model.user_model import User
from app.service.otp_service import OtpService
from app.service.email_service import EmailService

user_router = APIRouter(prefix="/users",tags=["Users"])

@user_router.post('/register')
async def register(
    user: UserCreate,
    background_task: BackgroundTasks,
    otp_service: OtpService = Depends(get_otp_service),
)->dict:
    otp = await otp_service.otp_generate_save('registration',user.email,user.model_dump())
    background_task.add_task(
        EmailService.send_otp_email,
        user.email,
        otp
    )
    return {
        "message":"Otp is Send to Email address."
    }
    
@user_router.post('/verify-register')
async def verify_register(
    user: VerifyRegister,
    background_task: BackgroundTasks,
    otp_service: OtpService = Depends(get_otp_service),
    user_service: UserService = Depends(get_user_service),
):
    user_data = await otp_service.verify_otp("registration",user.verify_email,user.otp)
    new_user = UserCreate(
        username=user_data.get("username"),
        email=user_data.get("email"),
        password=user_data.get("password")
    )
    await user_service.register_user(new_user)
    background_task.add_task(
        EmailService.send_register_success_email,
        new_user.username,
        new_user.email
    )
    return {"message": "Registration Sucessfuly please login to use the System."}

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

@user_router.post('/change-username',response_model=UserResponse)
async def change_username(
    username: UserUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
)->UserResponse:
    result = await service.change_username(username,user.id)
    return result

@user_router.post('/change-password',response_model=UserResponse)
async def change_password(
    userpassword: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
)->UserResponse:
    result = await service.change_password(userpassword,user.id)
    return result

@user_router.post('/change-email',response_model=UserResponse)
async def change_email(
    user_email: ChangeEmail,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
)->UserResponse:
    result = await service.change_email(user_email,user.id)
    return result

@user_router.post('/change-avaitar',response_model=UserResponse)
async def change_avaitar(
    avaitar: UploadFile,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
)->UserResponse:
    result = await service.change_avaitar(avaitar,user.id)
    return result