from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Flashcard, Question


LEITNER_INTERVALS = {
    1: 1,
    2: 3,
    3: 7,
    4: 14,
    5: 30,
}


def create_mistake_flashcard(db: Session, user_id: int, question: Question) -> Flashcard:
    card = Flashcard(
        user_id=user_id,
        front=f"{question.skill}: {question.prompt}",
        back=f"Correct answer: {question.correct_answer}\n\n{question.explanation}",
        category="mistake",
        leitner_box=1,
        due_at=datetime.now(UTC) + timedelta(days=1),
        source_question_id=question.id,
    )
    db.add(card)
    db.flush()
    return card


def review_flashcard(card: Flashcard, correct: bool) -> None:
    if correct:
        card.leitner_box = min(5, card.leitner_box + 1)
    else:
        card.leitner_box = 1
    card.due_at = datetime.now(UTC) + timedelta(days=LEITNER_INTERVALS[card.leitner_box])
