from fastapi import UploadFile, HTTPException, status
from app.core.config import setting
import os
import uuid
import aiofiles
class AvaitarStorageService:
    
    @staticmethod
    async def save_avaitar(self, file: UploadFile, user_id: uuid.UUID):
        if file.content_type not in setting.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{file.content_type}'. Allowed types: {', '.join(setting.ALLOWED_IMAGE_TYPES)}."
            )
        if file.size and file.size > setting.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of {setting.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )
        content = await file.read()
        if len(content) > setting.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of {setting.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )
        os.makedirs(setting.AVAITAR_S,exist_ok=True)
        file_extension = setting.MIME_TO_EXT.get(file.content_type)
        unique_filename = f"{setting.prefix}{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(setting.AVAITAR_S, unique_filename)
        async with aiofiles.open(file_path,"wb")as f:
            await f.write(content)
        new_avaitar_url = f"/{setting.AVAITAR_S.strip('/')}/{unique_filename}"
        return file_path, new_avaitar_url
    
    @staticmethod
    async def delete_avaitar(self, old_avaitar_url: str|None)->None:
        if not old_avaitar_url:
            return

        disk_path = old_avaitar_url.lstrip("/")
        if os.path.exists(disk_path) and os.path.isfile(disk_path):
            try:
                os.remove(disk_path)
            except OSError:
                pass