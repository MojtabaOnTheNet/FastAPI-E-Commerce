from fastapi import APIRouter, HTTPException
from ..dependency import CurrentUserDep, SessionDep
from ..schemas import *
from ..models import User
from ..core.security import password_hash

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me", status_code=200, response_model=UserPublic)
async def read_user(user: CurrentUserDep):
    return user

@router.put("/change_password", status_code=204)
async def change_user_password(user: CurrentUserDep, session: SessionDep, request_password_model: UserChangePassword):
    if not password_hash.verify(request_password_model.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password.")
    if request_password_model.new_password != request_password_model.confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    
    user.hashed_password = password_hash.hash(request_password_model.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)