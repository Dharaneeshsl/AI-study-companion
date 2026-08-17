import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from core.env import load_project_env
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_project_env()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required and must be set in environment.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """Validate the bearer token and confirm its user is still active in MongoDB."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("sub")
        if not user_id:
            raise credentials_exception

        from bson import ObjectId
        from database import database

        try:
            object_id = ObjectId(str(user_id))
        except Exception as exc:
            raise credentials_exception from exc

        user = await database.users.find_one({"_id": object_id})
        if not user or not user.get("is_active", True):
            raise credentials_exception
        return {"user_id": str(user["_id"]), "username": user.get("username", username)}
    except JWTError as exc:
        raise credentials_exception from exc
