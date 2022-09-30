from asyncio import current_task
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.future import select
from sqlalchemy.orm import Session, sessionmaker
from decouple import config
from server.schemas.unit import CreateUnit, ResponseUnit
from server.model.main import Unit
from fastapi.encoders import jsonable_encoder

router = APIRouter()

MYSQL_URL = config("MYSQL_URL")

engine = create_async_engine(MYSQL_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session() -> AsyncSession:
    sess = async_scoped_session(async_session, scopefunc=current_task)
    try:
        yield sess
    finally:
        await sess.close()

@router.post("/")
async def create_unit(unit_info: CreateUnit, db: AsyncSession = Depends(get_db_session)):
    unit = Unit(**unit_info.dict())
    db.add(unit)
    commit = await db.commit()
    refresh = await db.refresh(unit)
    return unit

@router.get("/")
async def get_all_unit(db: AsyncSession = Depends(get_db_session)):
    query = select(Unit)
    execute = await db.execute(query)
    result = execute.scalars().all()
    return result
