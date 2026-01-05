from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

from ..ai import ask_ai
from ..db import get_session
from ..deps import get_current_user
from ..models import ChatMessage, ChatScope, ChatThread, Role, User
from ..schemas import AIChatRequest, AIChatResponse, ChatMessageCreate, ChatMessageOut, ChatThreadCreate, ChatThreadOut

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, thread_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(thread_id, []).append(websocket)

    def disconnect(self, thread_id: int, websocket: WebSocket) -> None:
        if thread_id in self.active and websocket in self.active[thread_id]:
            self.active[thread_id].remove(websocket)

    async def broadcast(self, thread_id: int, message: dict) -> None:
        for ws in self.active.get(thread_id, []):
            await ws.send_json(message)


manager = ConnectionManager()


@router.post("/threads", response_model=ChatThreadOut)
def create_thread(payload: ChatThreadCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    thread = ChatThread(scope=payload.scope, subject=payload.subject, owner_id=user.id, audience=payload.audience)
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


@router.get("/threads", response_model=list[ChatThreadOut])
def list_threads(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(ChatThread)).all()


@router.post("/threads/{thread_id}/messages", response_model=ChatMessageOut)
def post_message(thread_id: int, payload: ChatMessageCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    thread = session.get(ChatThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    msg = ChatMessage(thread_id=thread_id, sender_id=user.id, role=user.role, body=payload.body)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


@router.websocket("/ws/chat/{thread_id}")
async def websocket_chat(websocket: WebSocket, thread_id: int, session: Session = Depends(get_session)):
    await manager.connect(thread_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            user_id = data.get("user_id")
            body = data.get("body", "")
            user = session.get(User, user_id) if user_id else None
            if not user:
                await websocket.send_json({"error": "Unknown user"})
                continue
            msg = ChatMessage(thread_id=thread_id, sender_id=user.id, role=user.role, body=body)
            session.add(msg)
            session.commit()
            session.refresh(msg)
            await manager.broadcast(thread_id, {"sender": user.name, "role": user.role, "body": body})
    except WebSocketDisconnect:
        manager.disconnect(thread_id, websocket)


@router.post("/ai", response_model=AIChatResponse)
async def ai_chat(payload: AIChatRequest):
    reply, provider = await ask_ai(payload.message, payload.syllabus_context)
    return AIChatResponse(reply=reply, provider=provider)
