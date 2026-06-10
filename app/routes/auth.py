from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from sqlmodel import select
from ..schemas import *
from ..models import *
from ..dependency import SessionDep
from ..core.security import *



router = APIRouter(prefix="/auth", tags=["Authentication"])


def authenticate_user(email: str, password: str, session: SessionDep) -> User | bool:
    user_db = session.exec(select(User).where(User.email == email)).first()
    if not user_db:
        return False
    if not password_hash.verify(password, user_db.hashed_password):
        return False
    return user_db

@router.post("/register", status_code=201, response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister):
    user = session.exec(select(User).where(User.email == user_in.email)).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )

    user_create = User.model_validate(user_in, update={"hashed_password": password_hash.hash(user_in.password)})
    session.add(user_create)
    session.commit()
    session.refresh(user_create)
    return user_create

@router.post("/token")
async def login_for_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(email=form_data.username.lower(), password=form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires)
    )
