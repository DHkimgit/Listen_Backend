from asyncio import current_task
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.future import select
from sqlalchemy.orm import Session, sessionmaker
from decouple import config
from server.schemas.user import CreateUsers
from server.model.user import Users
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

MYSQL_URL = config("MYSQL_URL")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = config("JWT_SECRET_KEY")  # should be kept secret
JWT_REFRESH_SECRET_KEY = config("JWT_REFRESH_SECRET_KEY")   # should be kept secret


engine = create_async_engine(MYSQL_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session() -> AsyncSession:
    sess = async_scoped_session(async_session, scopefunc=current_task)
    try:
        yield sess
    finally:
        await sess.close()

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def verify_password(password: str, hashed_pass: str) -> bool:
    return pwd_context.verify(password, hashed_pass)

@router.post("/")
async def post_user(user_info: CreateUsers, db: AsyncSession = Depends(get_db_session)):
    user_info.pw = pwd_context.hash(user_info.pw)
    user = Users(**user_info.dict())
    db.add(user)
    commit = await db.commit()
    refresh = await db.refresh(user)
    return user

@router.post('/login', summary="Create access and refresh tokens for user")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    query = select(Users).filter(Users.email == form_data.username)
    check_exist_user = await db.execute(query)

    if check_exist_user is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    else:
        objects = check_exist_user.scalars().one()
        user_info = jsonable_encoder(objects)
    
    hashed_pass = pwd_context.hash(form_data.password)

    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    token = create_access_token(user_info['email'])

    return f"Bearer {token}"