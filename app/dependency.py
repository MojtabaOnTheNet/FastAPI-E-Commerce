from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session
from .database import engine
from fastapi.security import OAuth2PasswordBearer
from .models import *
from .schemas import TokenPayload
import jwt
from .core.security import SECRET_KEY
from .core.security import ALGORITHM
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
import uuid

def get_session():
    with Session(engine) as session:
        yield session

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token"
)

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_bearer)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials.",
        )
    user = session.get(User, uuid.UUID(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUserDep) -> User:
    if current_user.is_superuser != 1:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user