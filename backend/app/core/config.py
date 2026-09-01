from pydantic_settings import BaseSettings , SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    APP_VERSION: str
    APP_TITLE: str
    DATABASE_URL: str
    SECRET_KEY: str
    REFERESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_TIME: int
    REFERESH_EXPIRY_TIME: int
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_HTTPONLY: bool = True
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024
    UPLOAD_DIR: str
    AVAITAR_S: str
    PREFIX: str
    REDIS_HOST: str
    REDIS_PORT: int 
    REDIS_DB: int
    REDIS_PASSWORD: str
    OTP_EXPIRY: int
    OTP_ATTEMPTS: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_FROM_NAME = "Task Management System"
    MAIL_SERVER = "smtp.google.com"
    MAIL_STARTTLS = True
    MAIL_SSL_TSL = False
    USE_CREDENTIALS = True
    VALIDATE_CERTS = True
    
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates" / "emails"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )
    @property
    def COOKIE_SETTING(self) -> dict:
        return {
            "httponly": self.COOKIE_HTTPONLY,
            "samesite": self.COOKIE_SAMESITE,
            "secure": self.COOKIE_SECURE,
        }
    @property
    def ALLOWED_IMAGE_TYPES(self)->dict:
        return {"image/jpeg", "image/png", "image/webp"}
    
    @property
    def MIME_TO_EXT(self)->dict:
        return {"image/jpeg":"jpeg", "image/png":"png", "image/webp":"webp"}
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
setting = Settings()