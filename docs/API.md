# API Reference (MVP)

Base URL: `http://localhost:8000/api`

## Auth
- `POST /auth/login` — OAuth2 password flow (form fields: `username`, `password`). Returns bearer token.

## Users
- `GET /users/me` — Current user profile.
- `POST /users` — Admin creates user (body: UserCreate).
- `GET /users?role=student&department=CS` — Admin or teacher lists users; teachers are limited to students.
- `PATCH /users/{id}` — Admin updates user fields.

## Change Requests
- `POST /change-requests` — Submit profile change request (any user).
- `GET /change-requests` — Admin list all.
- `GET /change-requests/mine` — Current user's requests.
- `POST /change-requests/{id}/review` — Admin approve/deny.

## Syllabus
- `POST /syllabus` — Teacher/Admin create item.
- `GET /syllabus?class_id=IX-A` — List items.
- `PATCH /syllabus/{id}` — Update status/fields.

## Quizzes
- `POST /quizzes/generate` — Teacher/Admin generate quiz from topics.
- `GET /quizzes?class_id=IX-A` — List quizzes.
- `POST /quizzes/{id}/attempts` — Student submits answers `{ "answers": {questionId: "choice"} }`.
- `GET /quizzes/analytics/weak-areas/{student_id}` — Compute weak areas.

## Chat
- `POST /chat/threads` — Create chat thread (class/teacher/ai scope).
- `GET /chat/threads` — List threads.
- `POST /chat/threads/{thread_id}/messages` — Post message to thread.
- `WS /chat/ws/chat/{thread_id}` — WebSocket for live chat (send JSON `{user_id, body}`).
- `POST /chat/ai` — AI chat endpoint `{ "message": "...", "syllabus_context": [] }`.

## Health
- `GET /health` — Service check.

## Notes
- Include `Authorization: Bearer <token>` header for protected routes.
- OpenAPI docs auto-available at `http://localhost:8000/docs`.
