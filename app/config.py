from typing import AnyStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DocuSign API credentials
    db_api_key: str
    base_path: str = "https://api.hellosign.com/v3"
    redirect_uri: str = "http://localhost:5173/setup/dropbox-sign"
    demo_docs_path: str = "./app/static/demo_documents/"

    class Config:
        env_file = ".env"

settings = Settings()