from sqlmodel import SQLModel , Field
from typing import Optional
from datetime import datetime 
import pytz

KST = pytz.timezone('Asia/Seoul')

class UnitBase(SQLModel):
    name: str
    member: int

class Unit(UnitBase, table=True):
    id: int = Field(default=None, primary_key=True)

class UnitCreate(UnitBase):
    pass

class UnitUpdate(UnitBase):
    pass

class User(SQLModel, table=True):
    service_number: Optional[str] = Field(default=None, primary_key=True)
    pw: Optional[str]
    name: Optional[str]
    rank: Optional[str]
    unit_id: Optional[int] = Field(default=None, foreign_key="unit.id")
    authority: Optional[str]

class PropositionBase(SQLModel):
    title: Optional[str]
    contents: Optional[str]
    status: Optional[str]

class Proposition(PropositionBase, table=True):
    proposal_id: int = Field(default=None, primary_key=True)
    writer: Optional[str] = Field(default=None, foreign_key="user.service_number")
    number_of_vote: int = Field(default=0, nullable=False)
    vote_status: Optional[str] = Field(default="투표중")
    frst_reg_date: datetime = Field(default=datetime.now(KST), nullable=False)
    last_chg_date: datetime = Field(default=datetime.now(KST), nullable=False)

class PropositionCreate(PropositionBase):
    pass
