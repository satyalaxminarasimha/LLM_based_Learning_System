from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user, require_role
from ..models import ChangeRequest, ChangeStatus, Role, User
from ..schemas import ChangeRequestCreate, ChangeRequestOut, ChangeRequestReview

router = APIRouter(prefix="/change-requests", tags=["change-requests"])


@router.post("/", response_model=ChangeRequestOut)
def submit_change_request(payload: ChangeRequestCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    cr = ChangeRequest(user_id=user.id, requested_changes=payload.requested_changes)
    session.add(cr)
    session.commit()
    session.refresh(cr)
    return cr


@router.get("/", response_model=list[ChangeRequestOut])
def list_requests(session: Session = Depends(get_session), _: User = Depends(require_role(Role.admin))):
    return session.exec(select(ChangeRequest)).all()


@router.post("/{request_id}/review", response_model=ChangeRequestOut)
def review_request(
    request_id: int,
    payload: ChangeRequestReview,
    session: Session = Depends(get_session),
    admin: User = Depends(require_role(Role.admin)),
):
    cr = session.get(ChangeRequest, request_id)
    if not cr:
        raise HTTPException(status_code=404, detail="Request not found")
    cr.status = payload.status
    cr.reviewer_id = admin.id
    cr.reviewer_note = payload.reviewer_note
    session.add(cr)
    session.commit()
    session.refresh(cr)
    return cr


@router.get("/mine", response_model=list[ChangeRequestOut])
def my_requests(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(ChangeRequest).where(ChangeRequest.user_id == user.id)).all()
