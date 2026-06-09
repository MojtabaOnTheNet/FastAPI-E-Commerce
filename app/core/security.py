from pwdlib import PasswordHash
from typing import Any, Annotated
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
import jwt
from .config import settings

SECRET_KEY = settings.SECRET_KEY

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

# subject has to be user id
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt