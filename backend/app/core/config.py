from pydantic_settings import BaseSettings , SettingsConfigDict

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
    
setting = Settings()