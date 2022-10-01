from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate
from server.db import init_db, get_session

router = APIRouter()

@router.get("/")
async def get_units(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Unit))
    units = result.scalars().all()
    return units

@router.get("/{unit_id}")
async def get_unit(unit_id:int , session: AsyncSession = Depends(get_session)):
    unit =  await session.get(Unit, unit_id)
    print(unit)
    if not unit :
        raise HTTPException(status_code=404)
    return unit

@router.post("/" , status_code= status.HTTP_201_CREATED)
async def add_unit (unit : UnitCreate , session : AsyncSession = Depends(get_session)):
    unit = Unit(name = unit.name , member= unit.member)
    session.add(unit)
    await session.commit()
    await session.refresh(unit)
    return unit

@router.patch("/{unit_id}" , response_model= Unit )
async def update_unit(unit_id:int , unit : UnitUpdate , session : AsyncSession = Depends(get_session)):
    db_unit = await session.get(Unit, unit_id)
    if not db_unit:
        raise HTTPException(status_code=404)
    unit_data  = unit.dict(exclude_unset=True)
    for key ,value in unit_data.items():
        setattr(db_unit ,key, value)
    session.add(db_unit)
    await session.commit()
    await session.refresh(db_unit)
    return db_unit

@router.delete("/{unit_id}")
async def delete_unit(unit_id: int, session : AsyncSession = Depends(get_session)):
    db_unit = await session.get(Unit, unit_id)
    if not db_unit:
        raise HTTPException(status_code=404)
    await session.delete(db_unit)
    await session.commit()
    return{"ok" : "true"}