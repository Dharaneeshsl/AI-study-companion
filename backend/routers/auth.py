import re
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from database import get_db
from schemas.user import Token, UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def _case_insensitive_exact(field: str, value: str) -> dict:
    return {field: {"$regex": f"^{re.escape(value)}$", "$options": "i"}}


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db=Depends(get_db)):
    normalized_username = user.username.strip()
    normalized_email = str(user.email).strip().lower()

    if await db.users.find_one(_case_insensitive_exact("email", normalized_email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await db.users.find_one(_case_insensitive_exact("username", normalized_username)):
        raise HTTPException(status_code=400, detail="Username already registered")

    user_dict = {
        "username": normalized_username,
        "email": normalized_email,
        "hashed_password": get_password_hash(user.password),
        "is_active": True,
    }
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return user_dict


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db),
):
    identifier = form_data.username.strip()
    user_dict = await db.users.find_one(
        {
            "$or": [
                _case_insensitive_exact("username", identifier),
                _case_insensitive_exact("email", identifier.lower()),
            ]
        }
    )

    if not user_dict or not user_dict.get("is_active", True) or not verify_password(
        form_data.password, user_dict["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user_dict["username"], "user_id": str(user_dict["_id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
