from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user, require_role
from ..models import Role, User
from ..schemas import UserCreate, UserOut, UserUpdate
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, session: Session = Depends(get_session), _: User = Depends(require_role(Role.admin))):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
        branch=payload.branch,
        classes=payload.classes,
        subjects=payload.subjects,
        roll_no=payload.roll_no,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
def list_users(
    role: Role | None = None,
    department: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if department:
        query = query.where(User.department == department)

    # Teachers can only view students (optionally filtered by department)
    if current_user.role == Role.teacher:
        query = query.where(User.role == Role.student)
    elif current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Not allowed")

    return session.exec(query).all()


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_session), _: User = Depends(require_role(Role.admin))):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
