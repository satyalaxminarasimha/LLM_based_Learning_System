# AI-Powered Learning System

FastAPI-based platform for admins, teachers, and students to manage users, syllabus, quizzes, AI/chat, and change requests. Swagger UI available at `/docs`.

## Features (MVP)
- Role-based auth (admin/teacher/student) with JWT.
- Admin: add teachers/students, edit details, handle change requests.
- Teacher: manage syllabus, view students, start class/subject chats, generate quizzes.
- Student: take quizzes, view results, weak areas, chat with teachers/AI, request profile updates.
- AI chat adapter (OpenAI-compatible) with offline stub fallback.
- WebSocket chat threads (class, teacher, AI contexts).

## Project Structure
- `backend/` FastAPI app (see `backend/app`).
- `docs/` SRS, architecture, API docs.
- Diagram: `Ai Powered Learning System(1).drawio`.

## Quickstart (Dev)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set JWT_SECRET and optional OPENAI_API_KEY
uvicorn app.main:app --reload
```
- Default admin: `admin@example.com` / `admin123` (override via env `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`).
- API base: `http://localhost:8000/api`. Swagger at `/docs`.

## Minimal Workflow
1) Login as admin → create teachers/students (`POST /api/users`).
2) Teachers add syllabus items (`POST /api/syllabus`) and generate quizzes (`POST /api/quizzes/generate`).
3) Students attempt quizzes (`POST /api/quizzes/{id}/attempts`), view weak areas (`GET /api/quizzes/analytics/weak-areas/{student_id}`).
4) Chat via `/api/chat/threads` + WebSocket `/api/chat/ws/chat/{thread_id}` or AI via `/api/chat/ai`.
5) Profile change requests: users submit `/api/change-requests`; admin reviews `/api/change-requests/{id}/review`.

## Testing Ideas
- Use `httpie`/`curl` for REST; `websocat` for WebSocket.
- Add pytest for services (not yet included).

## Deployment Notes
- Swap SQLite URL with Postgres in `.env` (`DB_URL=postgresql+psycopg2://user:pass@host/db`).
- Restrict `allow_origins` in `app.main` for production.
- Provide `OPENAI_API_KEY` to enable real AI responses.
