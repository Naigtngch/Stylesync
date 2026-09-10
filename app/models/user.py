from pydantic import BaseModel

class LoginPayModel(BaseModel):
    username: str
    password: str 