from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from decouple import config

ALGORITHM = "HS256"
JWT_SECRET_KEY = config("JWT_SECRET_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        service_number: str = payload.get("service_number")
        if service_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return service_number

async def get_current_servicenumber(service_number: str = Depends(get_current_user)):
    return service_number