import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .config import get_settings
from .db import engine, get_session, init_db
from .models import Role, User
from .routers import auth, change_requests, chat, quizzes, syllabus, users
from .security import hash_password

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(change_requests.router, prefix=settings.api_prefix)
app.include_router(syllabus.router, prefix=settings.api_prefix)
app.include_router(quizzes.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup():
    init_db()
    ensure_admin()


def ensure_admin():
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == admin_email)).first()
        if not existing:
            user = User(
                name="Admin",
                email=admin_email,
                phone=None,
                password_hash=hash_password(admin_password),
                role=Role.admin,
                department="Administration",
            )
            session.add(user)
            session.commit()


@app.get("/health")
def health():
    return {"status": "ok"}
