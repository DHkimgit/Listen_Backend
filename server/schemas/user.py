from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class CreateUser(BaseModel):
    name: str
    service_number: str
    email: str
    is_admin: bool

class ResponseUser(CreateUser):
    id: str

    class Config:
        orm_mode = True

class Status(str, Enum):
    admin = 'admin'
    normal = 'normal'

class CreateUsers(BaseModel):
    status: Status
    name: str
    email: str
    pw: str
    phone_number: str

