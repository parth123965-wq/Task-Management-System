from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    APP_VERSION: str
    APP_TITLE: str
    DATABASE_URL: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore'
    )
    
setting = Settings()