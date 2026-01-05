from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user, require_role
from ..models import Role, SyllabusItem, User
from ..schemas import SyllabusItemCreate, SyllabusItemOut, SyllabusItemUpdate

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("/", response_model=SyllabusItemOut)
def create_item(payload: SyllabusItemCreate, session: Session = Depends(get_session), teacher: User = Depends(require_role(Role.teacher, Role.admin))):
    item = SyllabusItem(
        class_id=payload.class_id,
        subject=payload.subject,
        topic=payload.topic,
        due_date=payload.due_date,
        teacher_id=teacher.id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/", response_model=list[SyllabusItemOut])
def list_items(class_id: str | None = None, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    query = select(SyllabusItem)
    if class_id:
        query = query.where(SyllabusItem.class_id == class_id)
    return session.exec(query).all()


@router.patch("/{item_id}", response_model=SyllabusItemOut)
def update_item(item_id: int, payload: SyllabusItemUpdate, session: Session = Depends(get_session), teacher: User = Depends(require_role(Role.teacher, Role.admin))):
    item = session.get(SyllabusItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(item, key, value)
    if payload.status == "completed" and not payload.completed_at:
        item.completed_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
