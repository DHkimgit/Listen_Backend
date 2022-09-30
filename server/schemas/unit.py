from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class CreateUnit(BaseModel):
    name: str
    member: int

class ResponseUnit(BaseModel):
    id: int
    name: str
    member: str