from asyncio import current_task
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.future import select
from sqlalchemy.orm import Session, sessionmaker
from decouple import config
from server.schemas.user import CreateUser, ResponseUser
from server.model.user import User
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
async def post_user(user_info: CreateUser, db: AsyncSession = Depends(get_db_session)):
    user = User(**user_info.dict())
    db.add(user)
    commit = await db.commit()
    refresh = await db.refresh(user)
    return user

@router.get("/")
async def get_all_user(db: AsyncSession = Depends(get_db_session)):
    query = select(User)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{id}")
async def get_user_from_id(id: str, db: AsyncSession = Depends(get_db_session)):
    query = select(User).filter(User.id == id)
    result = await db.execute(query)
    objects = result.scalars().one()
    print(jsonable_encoder(objects)['name'])
    return objects 