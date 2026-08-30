from app.repository.user_repository import UserRepository
from app.core.security import create_access_token, create_referesh_token, varify_password, hash_password
from app.schemas.user_schema import UserCreate, UserLogin, UserUpdate, ChangePasswordRequest, ChangeEmail
from fastapi import HTTPException, status, UploadFile
from app.model.user_model import User
import uuid
import aiofiles
import os
from app.core.config import setting

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
    
    async def change_username(self, update_data: UserUpdate, user_id: uuid.UUID)->User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="That user is Not found."
            )
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided to update."
            )
        if "username" in update_dict and update_dict["username"]:
            clean_username = update_dict["username"].strip()
            update_dict["username"] = clean_username

            if clean_username.lower() != user.username.lower():
                existing = await self.user_repo.get_by_username(clean_username)
                if existing and existing.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="That username is already taken."
                    )
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
    
    async def change_email(self, data: ChangeEmail, user_id: uuid.UUID)->User:
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
    
    async def change_avaitar(self, avaitar: UploadFile, user: User):
        if avaitar.content_type not in setting.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file type not match."
            )
        content = await avaitar.read()
        if len(content) > setting.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The Image size is too large."
            )
        os.makedirs(setting.AVAITAR_S,exist_ok=True)
        file_extension = avaitar.filename.split(".")[-1].lower() if avaitar.filename else "jpg"
        unique_filename = f"user_{user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(setting.AVAITAR_S, unique_filename)
        async with aiofiles.open(file_path,"wb")as f:
            await f.write(content)
        if user.avatar_url:
            exists = user.avatar_url.strip('/')
            if os.path.exists(exists):
                try:
                    os.remove(exists)
                except OSError:
                    pass
        avaitar_url = f"{setting.AVAITAR_S}/{unique_filename}"
        return await self.user_repo.update(user,{"avatar_url":avaitar_url})