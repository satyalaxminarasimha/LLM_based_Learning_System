from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..analytics import compute_weak_areas
from ..db import get_session
from ..deps import get_current_user, require_role
from ..models import Quiz, QuizAttempt, QuizQuestion, QuizResponse, Role, User, WeakArea
from ..quiz import attach_questions
from ..schemas import QuizAttemptCreate, QuizGenerateRequest, QuizOut, WeakAreaOut

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/generate", response_model=QuizOut)
def generate_quiz(payload: QuizGenerateRequest, session: Session = Depends(get_session), _: User = Depends(require_role(Role.teacher, Role.admin))):
    quiz = Quiz(class_id=payload.class_id, subject=payload.subject, generated_from={"topics": payload.topics})
    quiz = attach_questions(quiz, payload.topics, payload.num_questions)
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    return quiz


@router.get("/", response_model=list[QuizOut])
def list_quizzes(class_id: str | None = None, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    query = select(Quiz)
    if class_id:
        query = query.where(Quiz.class_id == class_id)
    return session.exec(query).all()


@router.post("/{quiz_id}/attempts")
def attempt_quiz(quiz_id: int, payload: QuizAttemptCreate, session: Session = Depends(get_session), student: User = Depends(require_role(Role.student))):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    attempt = QuizAttempt(quiz_id=quiz_id, student_id=student.id, started_at=datetime.utcnow())
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    questions = session.exec(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)).all()
    answers = payload.answers
    correct_count = 0
    responses: list[QuizResponse] = []
    for q in questions:
        choice = answers.get(q.id, "")
        is_correct = choice == q.answer
        if is_correct:
            correct_count += 1
        resp = QuizResponse(attempt_id=attempt.id, question_id=q.id, choice=choice, correct=is_correct, feedback=q.explanation)
        session.add(resp)
        responses.append(resp)

    attempt.submitted_at = datetime.utcnow()
    attempt.score = correct_count / max(len(questions), 1)
    session.add(attempt)
    session.commit()
    return {"attempt": attempt, "responses": responses}


@router.get("/analytics/weak-areas/{student_id}", response_model=list[WeakAreaOut])
def weak_areas(student_id: int, session: Session = Depends(get_session), _: User = Depends(require_role(Role.teacher, Role.admin, Role.student))):
    return compute_weak_areas(session, student_id)
