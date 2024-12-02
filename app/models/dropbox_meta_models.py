from pydantic import BaseModel

class UpdateDropboxSignConfigRequest(BaseModel):
    api_key: str