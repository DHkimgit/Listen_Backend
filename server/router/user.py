from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate, User, Proposition
from server.db import init_db, get_session
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def user_info(name, service_number, rank, unit_name, authority) -> dict:
    return {
        "name": name,
        "service_number": service_number,
        "rank": rank,
        "unit": unit_name,
        "authority": authority
    }

@router.post("/")
async def add_user(user: User, session: AsyncSession = Depends(get_session)):
    unit =  await session.get(Unit, user.unit_id)
    user_exist = await session.get(User, user.service_number)
    if user_exist:
        raise HTTPException(status_code=404)
    if not unit :
        raise HTTPException(status_code=404)
    hashed_pw = pwd_context.hash(user.pw, salt="IwoeifhcnjdhFkIeJmdkfi")
    user = User(service_number = user.service_number, pw = hashed_pw, name = user.name, rank = user.rank, unit_id = user.unit_id, authority = user.authority)
    db_unit = await session.get(Unit, user.unit_id)
    current_number_of_unit_mamber = db_unit.member
    setattr(db_unit ,'member', current_number_of_unit_mamber + 1)
    session.add(user)
    session.add(db_unit)
    await session.commit()
    await session.refresh(user)
    await session.refresh(db_unit)
    return user

@router.get("/user_info/{service_number}")
async def user_information(service_number: str, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, service_number)
    if user == None:
        raise HTTPException(status_code=404)
    unit = await session.get(Unit, user.unit_id)
    result = user_info(user.name, user.service_number, user.rank, unit.name, user.authority)
    return result

@router.delete("/{service_number}")
async def delete_user(service_number: str, session : AsyncSession = Depends(get_session)):
    db_user = await session.get(User, service_number)
    if db_user == None:
        raise HTTPException(status_code=404)
    await session.delete(db_user)
    await session.commit()
    return{"ok" : "true"}
