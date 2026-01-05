from collections import Counter, defaultdict
from typing import List

from sqlalchemy import delete
from sqlmodel import Session, select

from .models import QuizAttempt, QuizQuestion, QuizResponse, WeakArea


def compute_weak_areas(session: Session, student_id: int) -> List[WeakArea]:
    attempts = session.exec(select(QuizAttempt).where(QuizAttempt.student_id == student_id)).all()
    if not attempts:
        return []

    topic_errors: Counter[str] = Counter()
    evidence_map: defaultdict[str, list[int]] = defaultdict(list)

    for attempt in attempts:
        responses = session.exec(select(QuizResponse).where(QuizResponse.attempt_id == attempt.id)).all()
        for resp in responses:
            question = session.get(QuizQuestion, resp.question_id)
            topic = question.topic or "general"
            if not resp.correct:
                topic_errors[topic] += 1
                evidence_map[topic].append(question.id)

    # Clear previous computed weak areas for simplicity
    session.exec(delete(WeakArea).where(WeakArea.student_id == student_id))

    weak_areas: List[WeakArea] = []
    for topic, count in topic_errors.items():
        severity = min(1.0, count / 5)
        wa = WeakArea(student_id=student_id, topic=topic, severity=severity, evidence={"questions": evidence_map[topic]})
        session.add(wa)
        weak_areas.append(wa)
    session.commit()
    return weak_areas
