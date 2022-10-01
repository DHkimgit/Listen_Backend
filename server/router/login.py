from asyncio import current_task
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate, User
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from decouple import config
from server.db import init_db, get_session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
JWT_SECRET_KEY = config("JWT_SECRET_KEY")

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def verify_password(password: str, hashed_pass: str) -> bool:
    if password==hashed_pass:
        return True
    else:
        return False
    # return pwd_context.verify(password, hashed_pass)

def user_info(name, service_number, rank, unit_name, authority) -> dict:
    return {
        "name": name,
        "service_number": service_number,
        "rank": rank,
        "unit": unit_name,
        "authority": authority
    }

@router.post('/login', summary="Create access and refresh tokens for user")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await session.get(User, form_data.username)
    print(user)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Incorrect email or password"
        )
    
    hashed_pass = pwd_context.hash(form_data.password, salt="IwoeifhcnjdhFkIeJmdkfi")
    print(hashed_pass)
    print(user.pw)
    result = verify_password(user.pw, hashed_pass)
    print(result)
    if not verify_password(user.pw, hashed_pass):
        raise HTTPException(
            status_code=404,
            detail="Incorrect email or password1"
        )
    
    unit = await session.get(Unit, user.unit_id)

    encode_data = user_info(user.name, user.service_number, user.rank, unit.name, user.authority)
    encoded_jwt = jwt.encode(encode_data, JWT_SECRET_KEY, ALGORITHM)

    return f"{encoded_jwt}"
# f"Bearer {encoded_jwt}"

@router.post('/token', summary="Create access and refresh tokens for user")
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await session.get(User, form_data.username)
    print(user)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Incorrect email or password"
        )
    
    hashed_pass = pwd_context.hash(form_data.password, salt="IwoeifhcnjdhFkIeJmdkfi")
    print(hashed_pass)
    print(user.pw)
    result = verify_password(user.pw, hashed_pass)
    print(result)
    if not verify_password(user.pw, hashed_pass):
        raise HTTPException(
            status_code=404,
            detail="Incorrect email or password1"
        )
    
    unit = await session.get(Unit, user.unit_id)

    encode_data = user_info(user.name, user.service_number, user.rank, unit.name, user.authority)
    encoded_jwt = jwt.encode(encode_data, JWT_SECRET_KEY, ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer"}