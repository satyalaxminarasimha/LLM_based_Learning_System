from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field

from .models import ChangeStatus, ChatScope, Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    role: Role


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: Role
    department: Optional[str] = None
    branch: Optional[str] = None
    classes: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    roll_no: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    branch: Optional[str] = None
    classes: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    roll_no: Optional[str] = None
    active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    role: Role
    department: Optional[str]
    branch: Optional[str]
    classes: Optional[List[str]]
    subjects: Optional[List[str]]
    roll_no: Optional[str]
    active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class ChangeRequestCreate(BaseModel):
    requested_changes: dict[str, Any]


class ChangeRequestReview(BaseModel):
    status: ChangeStatus
    reviewer_note: Optional[str] = None


class ChangeRequestOut(BaseModel):
    id: int
    user_id: int
    requested_changes: dict[str, Any]
    status: ChangeStatus
    reviewer_id: Optional[int]
    reviewer_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SyllabusItemCreate(BaseModel):
    class_id: str
    subject: str
    topic: str
    due_date: Optional[datetime] = None


class SyllabusItemUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SyllabusItemOut(BaseModel):
    id: int
    class_id: str
    subject: str
    topic: str
    status: str
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    teacher_id: Optional[int]

    class Config:
        orm_mode = True


class QuizGenerateRequest(BaseModel):
    class_id: str
    subject: str
    topics: List[str] = Field(default_factory=list)
    num_questions: int = 5


class QuizQuestionOut(BaseModel):
    id: int
    prompt: str
    options: List[str]
    explanation: str
    topic: Optional[str]

    class Config:
        orm_mode = True


class QuizOut(BaseModel):
    id: int
    class_id: str
    subject: str
    generated_from: dict[str, Any]
    created_at: datetime
    questions: List[QuizQuestionOut]

    class Config:
        orm_mode = True


class QuizAttemptCreate(BaseModel):
    answers: dict[int, str]


class QuizAttemptOut(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[float]

    class Config:
        orm_mode = True


class WeakAreaOut(BaseModel):
    id: int
    student_id: int
    topic: str
    severity: float
    evidence: dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class ChatThreadCreate(BaseModel):
    scope: ChatScope
    subject: Optional[str] = None
    audience: dict[str, Any] = Field(default_factory=dict)


class ChatThreadOut(BaseModel):
    id: int
    scope: ChatScope
    subject: Optional[str]
    audience: dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class ChatMessageCreate(BaseModel):
    body: str


class ChatMessageOut(BaseModel):
    id: int
    thread_id: int
    sender_id: int
    role: Role
    body: str
    created_at: datetime

    class Config:
        orm_mode = True


class AIChatRequest(BaseModel):
    message: str
    syllabus_context: Optional[list[str]] = None


class AIChatResponse(BaseModel):
    reply: str
    provider: str
