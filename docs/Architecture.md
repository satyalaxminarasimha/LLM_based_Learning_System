# Architecture & Implementation Plan

## 1. High-Level Architecture
- **Frontend:** React (Vite, TypeScript), component library (Mantine/Chakra-free styling), WebSocket for chat, REST for CRUD, protected routes per role.
- **Backend:** FastAPI (Python), JWT auth, SQLModel/SQLAlchemy with SQLite for dev and PostgreSQL-ready. Celery/BackgroundTasks for quiz generation and AI fallbacks.
- **AI Adapter:** Pluggable provider (OpenAI-compatible) via environment variable; fallback deterministic stub for offline/dev.
- **Real-time:** FastAPI WebSocket endpoints; per-thread authorization.
- **Storage:** Relational DB for users/quizzes/chats/syllabus; Redis optional for websocket presence and rate limits.

## 2. Services / Modules
- `auth`: signup/import by admin, login, JWT issuance/refresh, password hashing.
- `users`: CRUD for teachers/students, role assignment, profile update requests, approval workflow.
- `syllabus`: Track topics per class/subject; update completion; feed quiz generator.
- `quiz`: Generate quizzes from syllabus + weak areas; store attempts and responses; compute scores/explanations.
- `analytics`: Derive weak areas from attempts; expose summaries per student/topic.
- `chat`: Thread + message model; class/teacher public chats; AI chat bridging to provider; rate limiting.
- `notifications`: Email/webhook stub; in-app notifications for status changes.

## 3. Data Model (tables)
- User(id, name, email, phone, password_hash, role, department, branch, classes, subjects, roll_no, active, created_at, updated_at)
- ChangeRequest(id, user_id, requested_changes JSON, status, reviewer_id, reviewer_note, created_at, updated_at)
- SyllabusItem(id, class_id, subject, topic, status, due_date, completed_at, teacher_id)
- Quiz(id, class_id, subject, generated_from JSON, created_at)
- QuizQuestion(id, quiz_id, prompt, options[], answer, explanation, topic)
- QuizAttempt(id, quiz_id, student_id, started_at, submitted_at, score)
- QuizResponse(id, attempt_id, question_id, choice, correct, feedback)
- WeakArea(id, student_id, topic, severity, evidence JSON)
- ChatThread(id, scope (class|teacher|ai), subject, owner_id, audience JSON, created_at)
- ChatMessage(id, thread_id, sender_id, role, body, created_at)

## 4. API Surface (initial)
- `/auth/login`, `/auth/refresh`
- `/users` (admin create/list/update), `/users/{id}`
- `/change-requests` (submit by teacher/student), `/change-requests/{id}` (admin review)
- `/syllabus` (CRUD), `/syllabus/{id}/complete`
- `/quizzes` (generate), `/quizzes/{id}`, `/quizzes/{id}/attempts`, `/attempts/{id}`
- `/analytics/weak-areas/{student_id}`
- `/chat/threads` (list/create), `/chat/threads/{id}/messages` (REST) and `/ws/chat/{thread_id}` (WebSocket)
- `/ai/chat` (stream/fallback)

## 5. Security & Compliance
- JWT with role claims; per-endpoint dependency checks.
- Password hashing (argon2/bcrypt); strong validation; audit log for admin changes.
- Input size limits; rate limits on chat/quiz generation; CORS locked to frontend origin.
- PII minimization in logs; secrets via env vars (`OPENAI_API_KEY`, `JWT_SECRET`, `DB_URL`).

## 6. Deployment Plan
- Dev: Docker Compose (FastAPI + SQLite volume; optional Redis), Vite dev server.
- Prod: Postgres + FastAPI behind reverse proxy; static frontend build served via CDN or gateway.
- Observability: Structured logging (JSON), request ids, basic health check `/health`.

## 7. Testing Strategy
- Backend: pytest for services, API tests with TestClient, data factories; property tests for quiz scoring.
- Frontend: Vitest + Testing Library for components and hooks.
- E2E: Playwright basic flows (login, quiz, chat).

## 8. Delivery Phases (repo tasks)
1) Bootstrap repo (backend + frontend folders, tooling, env example).
2) Implement auth + user management + change requests.
3) Syllabus + quiz generation + attempts + analytics.
4) Chat (AI + class/teacher channels) via WebSocket.
5) Polish: notifications stub, docs, tests, Docker Compose.

## 9. Documentation Plan
- `README.md`: quickstart, env vars, run commands, architecture sketch.
- `docs/SRS.md`: requirements (this SRS).
- `docs/Architecture.md`: this plan + updates.
- `docs/API.md`: endpoint details (to be added after implementation).
