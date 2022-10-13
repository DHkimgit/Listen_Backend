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
    proposition_total: int = Field(default=0)

class UnitCreate(UnitBase):
    pass

class UnitUpdate(UnitBase):
    pass

class Propositionstatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str]

class Votestatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str]

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

class PropositionUpdate(SQLModel):
    contents: str

class Proposition(PropositionBase, table=True):
    proposal_id: int = Field(default=None, primary_key=True)
    writer: Optional[str] = Field(default=None, foreign_key="user.service_number")
    status: Optional[int] = Field(default=1, foreign_key="propositionstatus.id")
    answer_status: Optional[int] = Field(default=1, foreign_key="answerstatus.id")
    vote_favor: int = Field(default=0, nullable=False)
    vote_against: int = Field(default=0, nullable=False)
    vote_status: Optional[int] = Field(default=1, foreign_key="votestatus.id")
    frst_reg_date: datetime = Field(default=datetime.now(KST), nullable=False)
    last_chg_date: datetime = Field(default=datetime.now(KST), nullable=False)

class PropositionCreate(PropositionBase):
    pass

class Votetype(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str 

class Uservote(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    proposal_id: int = Field(default=None, foreign_key="proposition.proposal_id")
    voter: Optional[str] = Field(default=None, foreign_key="user.service_number")
    vote_type: int = Field(default=None, foreign_key="votetype.id")

class PropositioncommentBase(SQLModel):
    contents: Optional[str]

class Propositioncomment(PropositioncommentBase, table=True):
    comment_id: int = Field(default=None, primary_key=True)
    commenter: Optional[str] = Field(default=None, foreign_key="user.service_number")
    proposal_id: int = Field(default=None, foreign_key="proposition.proposal_id")
    comment_date: datetime = Field(default=datetime.now(KST), nullable=False)

class PropositioncommentCreate(PropositioncommentBase):
    pass

class PropositionanswerBase(SQLModel):
    title: Optional[str]
    contents: Optional[str]
    
class Propositionanswer(PropositionanswerBase, table=True):
    answer_id: int = Field(default=None, primary_key=True)
    proposal_id: int = Field(default=None, foreign_key="proposition.proposal_id")
    writer: str = Field(default=None, foreign_key="user.service_number")
    frst_reg_date: datetime = Field(default=datetime.now(KST), nullable=False)
    last_chg_date: datetime = Field(default=datetime.now(KST), nullable=False)

class PropositionanswerCreate(PropositionanswerBase):
    pass
    
class Propositionstorage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user: str = Field(default=None, foreign_key="user.service_number")
    proposal_id: int = Field(default=None, foreign_key="proposition.proposal_id")
    unit_id: int = Field(default=None, foreign_key="unit.id")

class Answerstatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str