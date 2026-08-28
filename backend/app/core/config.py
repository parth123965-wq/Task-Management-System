from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    APP_VERSION: str
    APP_TITLE: str
    DATABASE_URL: str
    SECRET_KEY: str
    REFERESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_TIME: str
    ACCESS_TOKEN_EXPIRY_TIME_FOR_REFERESH_TOKEN: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore'
    )
    
setting = Settings()