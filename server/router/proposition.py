from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate, PropositionBase, Proposition, PropositionCreate
from server.db import init_db, get_session
from server.auth.token import get_current_servicenumber, get_current_user
router = APIRouter()

@router.post("/")
async def add_proposition(prop: PropositionCreate, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = Proposition(writer = service_number, title = prop.title, contents = prop.contents, status = prop.status)
    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)
    return proposal

@router.get("/me")
async def get_active_user_proposition(session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    query = select(Proposition).where(Proposition.writer == service_number)
    prop = await session.execute(query)
    if prop == None:
        raise HTTPException(status_code=404)
    result = prop.scalars().all()
    return result

@router.get("/{service_number}")
async def get_proposition(service_number: str, session: AsyncSession = Depends(get_session)):
    query = select(Proposition).where(Proposition.writer == service_number)
    prop = await session.execute(query)
    if prop == None:
        raise HTTPException(status_code=404)
    result = prop.scalars().all()
    return result

