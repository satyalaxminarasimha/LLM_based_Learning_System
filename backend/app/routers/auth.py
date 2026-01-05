from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from .. import security
from ..config import get_settings
from ..db import get_session
from ..models import User
from ..schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    token = security.create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token)
