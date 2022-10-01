from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from decouple import config
from server.model.user import User
from server.schemas.user import CreateUser

MYSQL_URL = config("MYSQL_URL")
# engine = create_async_engine(MYSQL_URL, echo=True)
# async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# session = async_scoped_session(async_session, scopefunc=current_task)

# async def get_db_session() -> AsyncSession:
#     sess = AsyncSession(bind=engine)
#     try:
#         yield sess
#     finally:
#         await sess.close()
engine = create_async_engine('mysql+aiomysql://admins:0000@52.79.112.41:59782/LISTEN', echo=True)

async def get_db_session() -> AsyncSession:
    sess = AsyncSession(bind=engine)
    try:
        yield sess
    finally:
        await sess.close()

# async def create_user(session: session, user_info : CreateUser):
#     user_details = session.query(User).filter(user_info.service_number == User.service_number, user_info.name == User.name).first()

#     new_user_info = User(**user_info.dict())
#     session.add(new_user_info)
#     session.commit()
#     session.refresh(new_user_info)

#     return new_user_info
