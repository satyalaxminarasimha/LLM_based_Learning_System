# Software Requirements Specification (SRS)

## 1. Introduction
- **Product name:** AI-Powered Learning System
- **Purpose:** Provide an AI-assisted platform for administrators, teachers, and students to manage learning content, communicate, and personalize assessments.
- **Scope:** User management, syllabus tracking, quiz generation/evaluation, AI chat assistance, role-based communication, analytics on weak areas, and change-request workflows.
- **Users:** Admin, Teacher, Student.
- **Assumptions:** Internet access for AI calls; SMTP/notification provider available; single institution deployment by default.

## 2. Overall Description
- **Product perspective:** Web application with REST/WebSocket APIs, AI assistant service, and relational database.
- **User classes & characteristics:**
  - Admin: manages users, roles, profile updates, reviews change requests.
  - Teacher: updates syllabus, views students, chats with students, requests admin changes.
  - Student: takes quizzes, views results/weak areas, chats with AI/teachers, requests updates.
- **Operating environment:** Modern browser; backend on Linux; database (PostgreSQL/SQLite for dev); AI provider (OpenAI-compatible) via HTTP API.
- **Constraints:** Role-based access control (RBAC); PII protection; audit logging for profile changes; quizzes must be traceable to syllabus coverage.

## 3. Functional Requirements
### 3.1 Authentication & Authorization
- Users sign in with email/password; roles determine permissions (Admin, Teacher, Student).
- Passwords stored hashed; sessions via JWT/HTTP-only cookies.

### 3.2 User Management (Admin)
- Add teacher with fields: name, email, password, phone, classes taught, subjects, role, department.
- Add student with fields: name, email, password, phone, roll number, branch, role.
- View/update details of teachers and students.
- Assign/update roles to teachers; deactivate/reactivate accounts.

### 3.3 Change Requests
- Teachers/students can submit change requests for their details.
- Admin reviews requests, approves/denies, and responds with a message.
- Users can view status of their requests.

### 3.4 Syllabus Management (Teacher)
- Update daily syllabus progress by marking topics complete.
- Maintain per-class/course syllabus with status and dates.

### 3.5 Student Insights (Teacher)
- View students of same department/class and their scores, profiles, rankings.
- Filter by class/year/session.

### 3.6 Communication
- **Public chat (Teacher ⇄ Students):** One session per class/year; text threads archived.
- **Public chat (Student ⇄ Teacher):** Subject-wise channels; students can post questions; teachers reply.
- **AI chat (all roles):** Ask questions; AI answers using course syllabus/context when available.
- **Notifications:** When change requests are processed, quiz results ready, or chats mentioned.

### 3.7 Assessments
- Generate quizzes based on completed syllabus topics and students’ weak areas.
- Students attempt quizzes; time limits; randomized questions.
- Students view results and explanations for each answer.
- System analyzes results to identify weak areas by topic/subject/prerequisites.

### 3.8 Profiles
- Students view/update their profile (non-privileged fields) and see history of quizzes, ranks, weak areas.
- Teachers view their teaching assignments and syllabus progress.

## 4. Non-Functional Requirements
- **Security:** Hash passwords (argon2/bcrypt); enforce RBAC; validate inputs; rate-limit auth and chat/quiz generation; audit trails for profile changes and admin actions.
- **Performance:** ≤300ms p95 for standard API calls; chats streamed; quizzes generated within 5s (with async job fallback).
- **Availability:** Target 99% for MVP; graceful degradation if AI provider unavailable (use fallback canned responses).
- **Scalability:** Stateless API; WebSocket gateway; database indexing on user/role/class.
- **Usability:** Responsive UI; accessible (WCAG AA targets); clear role separation.
- **Maintainability:** Modular services (auth, user, syllabus, quiz, chat, analytics); typed APIs; automated tests.
- **Privacy/Compliance:** Minimize PII exposure; allow account deactivation; log access to sensitive fields.

## 5. Data Requirements (initial)
- User {id, name, email, phone, password_hash, role, department/branch, classes, subjects, roll_no, active, created_at}
- ChangeRequest {id, user_id, requested_changes (json), status, reviewer_id, reviewer_note, created_at, updated_at}
- SyllabusItem {id, class_id, subject, topic, status, due_date, completed_at, teacher_id}
- Quiz {id, class_id, subject, topic_ids[], generated_from, created_at}
- QuizQuestion {id, quiz_id, prompt, options, answer, explanation, topic_id}
- QuizAttempt {id, quiz_id, student_id, started_at, submitted_at, score}
- QuizResponse {attempt_id, question_id, choice, correct, feedback}
- WeakArea {student_id, topic_id, severity, evidence (attempt refs)}
- ChatThread {id, scope (class|teacher|ai), subject, owner_id, audience (class/year), created_at}
- ChatMessage {id, thread_id, sender_id, role, body, created_at}

## 6. External Interfaces
- **REST API:** JSON over HTTPS for CRUD and assessments.
- **WebSocket:** Real-time chat; live quiz timer updates.
- **AI Provider:** OpenAI-compatible completion/chat endpoint; pluggable via adapter.
- **Email/Notification:** SMTP or webhook-based notification.

## 7. Use Cases (from diagram & derived)
- Admin: add teacher; add student; view/update user; assign roles; view/respond change requests; AI chat.
- Teacher: AI chat; view students; chat with students; request profile changes; update syllabus; public chats per class; view rankings.
- Student: AI chat; view profile; attempt quiz; view results; see weak areas; chat with teachers; request profile changes; class chats.

## 8. Error Handling & Edge Cases
- AI provider down → cached/fallback responses with warning.
- Quiz generation timeout → queued job and notify user when ready.
- Concurrent profile edits → optimistic locking with `updated_at` check.
- Chat abuse → rate limits and max message length; moderation hook placeholder.

## 9. Acceptance Criteria (MVP)
- Role-based login working for all roles.
- Admin can create users and approve change requests; updates persist.
- Teacher can update syllabus and see roster; students see updated syllabus-dependent quizzes.
- Student can attempt generated quiz, see scored results and weak-area summary.
- Chat works for AI (with fallback) and class/teacher channels via WebSocket.
- Documentation and API reference available in repository.

## 10. Future Enhancements
- File uploads (notes, assignments), calendar, grading imports, mobile app, analytics dashboard, SSO (OAuth/SAML), LTI integration, content recommendation, plagiarism checks.
