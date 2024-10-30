from typing import AnyStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DocuSign API credentials
    db_api_key: str
    db_api_app_id: str

    class Config:
        env_file = ".env"

settings = Settings()