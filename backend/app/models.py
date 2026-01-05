from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from sqlmodel import Column, DateTime, Field, JSON, Relationship, SQLModel


class Role(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class ChangeStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class ChatScope(str, Enum):
    class_channel = "class"
    teacher_channel = "teacher"
    ai = "ai"


class UserBase(SQLModel):
    name: str
    email: str = Field(index=True)
    phone: str | None = None
    role: Role = Role.student
    department: str | None = None
    branch: str | None = None
    classes: List[str] | None = Field(default=None, sa_column=Column(JSON))
    subjects: List[str] | None = Field(default=None, sa_column=Column(JSON))
    roll_no: str | None = Field(default=None, index=True)
    active: bool = True


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["ChatMessage"] = Relationship(back_populates="sender")


class ChangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    requested_changes: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: ChangeStatus = ChangeStatus.pending
    reviewer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewer_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SyllabusItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: str
    subject: str
    topic: str
    status: str = "pending"
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    teacher_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: str
    subject: str
    generated_from: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    questions: List["QuizQuestion"] = Relationship(back_populates="quiz")


class QuizQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    prompt: str
    options: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    answer: str
    explanation: str
    topic: Optional[str] = None

    quiz: Quiz = Relationship(back_populates="questions")


class QuizAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    student_id: int = Field(foreign_key="user.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None


class QuizResponse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="quizattempt.id")
    question_id: int = Field(foreign_key="quizquestion.id")
    choice: str
    correct: bool
    feedback: Optional[str] = None


class WeakArea(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id")
    topic: str
    severity: float = 0.0
    evidence: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatThread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    scope: ChatScope
    subject: Optional[str] = None
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    audience: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["ChatMessage"] = Relationship(back_populates="thread")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="chatthread.id")
    sender_id: int = Field(foreign_key="user.id")
    role: Role
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    thread: ChatThread = Relationship(back_populates="messages")
    sender: User = Relationship(back_populates="messages")
