from app.repository.user_repository import UserRepository
from app.core.security import create_access_token, create_referesh_token, varify_password, hash_password
from app.schemas.user_schema import UserCreate, UserLogin, UserUpdate, ChangePasswordRequest, ChangeEmail
from fastapi import HTTPException, status
from app.model.user_model import User
import uuid

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_user(self, data: UserCreate)->User:
        if await self.user_repo.get_by_email(email=data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That Email is Already Register."
            )
        if await self.user_repo.get_by_username(username=data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That Username is Already Register."
            )
        password = hash_password(data.password)
        new_user = User(
            username=data.username,
            email=data.email,
            hashed_password=password
        )
        return await self.user_repo.create(new_user)
    
    async def login_user(self, data: UserLogin)->tuple[str, str]:
        user =  await self.user_repo.get_by_identifier(data.identifier)
        if not user or not varify_password(data.password,user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Cradincials"
            )
        access_token = create_access_token(user.id)
        referesh_token = create_referesh_token(user.id)
        return access_token, referesh_token
    
    async def user_profile_update(self, update_data: UserUpdate, user_id: uuid.UUID)->User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="That user is Not found."
            )
        if update_data.username and update_data.username!=user.username:
            existing = await self.user_repo.get_by_username(update_data.username)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="That Username is alreay taken."
                )
        update_dict = update_data.model_dump(exclude_unset=True)
        return await self.user_repo.update(user,update_dict)
    
    async def change_password(self, data: ChangePasswordRequest, user_id: uuid.UUID)->User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="That User is not Found."
            )
        if not varify_password(data.current_password,user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password not match."
            )
        if data.current_password==data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both password is same."
            )
        updated = {"hashed_password":hash_password(data.new_password)}
        result = await self.user_repo.update(user,updated)
        return result
    
    async def change_email(self, data: ChangeEmail, user_id: uuid.UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="That User is not Found."
            )
        if data.new_email==user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both email is same."
            )
        exist = await self.user_repo.get_by_email(data.new_email)
        if exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That email is already Registerd."
            )
        updated = {"email":data.new_email}
        result = await self.user_repo.update(user,updated)
        return result