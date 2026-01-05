import random
from typing import List

from .models import Quiz, QuizQuestion


QUIZ_TEMPLATES = [
    "Which of the following is true about {topic}?",
    "Identify the best explanation for {topic}.",
    "Select the correct statement related to {topic}.",
    "A common mistake about {topic} is?",
]


def synthesize_options(topic: str) -> list[str]:
    correct = f"Core fact about {topic}"
    distractors = [
        f"Irrelevant detail about {topic}",
        f"Common misconception about {topic}",
        f"Edge case related to {topic}",
    ]
    random.shuffle(distractors)
    options = [correct] + distractors
    random.shuffle(options)
    return options


def generate_questions(topics: List[str], num_questions: int) -> list[QuizQuestion]:
    selected = (topics or ["general principle"]) * 1
    pool = selected[:]
    random.shuffle(pool)
    questions: list[QuizQuestion] = []
    for i in range(num_questions):
        topic = pool[i % len(pool)] if pool else "general"
        prompt = random.choice(QUIZ_TEMPLATES).format(topic=topic)
        options = synthesize_options(topic)
        answer = f"Core fact about {topic}"
        explanation = f"We expect recall of key concept for {topic}."
        questions.append(
            QuizQuestion(prompt=prompt, options=options, answer=answer, explanation=explanation, topic=topic)
        )
    return questions


def attach_questions(quiz: Quiz, topics: List[str], num_questions: int) -> Quiz:
    quiz.questions = generate_questions(topics, num_questions)
    return quiz
