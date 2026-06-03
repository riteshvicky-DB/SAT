import json as _json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Answer, Flashcard, Question, User
from app.services.spaced_repetition import review_flashcard

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("")
def list_flashcards(
    due_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    now = datetime.now(UTC).replace(tzinfo=None)
    query = select(Flashcard).where(Flashcard.user_id == current_user.id)
    if due_only:
        query = query.where(Flashcard.due_at <= now)
    cards = db.execute(query.order_by(Flashcard.due_at.asc()).limit(50)).scalars().all()
    return {"cards": [_card_payload(c, now) for c in cards], "total": len(cards)}


@router.post("/{card_id}/review")
def review_card(
    card_id: int,
    correct: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    card = db.get(Flashcard, card_id)
    if card is None or card.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    review_flashcard(card, correct)
    db.commit()
    return {"id": card.id, "leitner_box": card.leitner_box, "due_at": card.due_at.isoformat()}


@router.get("/mistakes")
def list_mistakes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.execute(
        select(Answer, Question)
        .join(Question, Answer.question_id == Question.id)
        .where(Answer.user_id == current_user.id, Answer.is_correct.is_(False))
        .order_by(Answer.answered_at.desc())
        .limit(50)
    ).all()
    mistakes = []
    for answer, question in rows:
        from app.services.video_map import get_video_url, is_search_url
        vurl = get_video_url(question.skill, question.section)
        mistakes.append({
            "answer_id": answer.id,
            "answered_at": answer.answered_at.isoformat(),
            "selected_answer": answer.selected_answer,
            "seconds_spent": answer.seconds_spent,
            "question": {
                "id": question.id,
                "section": question.section,
                "domain": question.domain,
                "skill": question.skill,
                "difficulty": question.difficulty,
                "prompt": question.prompt,
                "passage": question.passage,
                "choices": _json.loads(question.choices_json or "[]"),
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "video_url": vurl,
                "video_label": "Search SAT Tutorial" if is_search_url(vurl) else "Watch SAT Tutorial",
            },
        })
    return {"mistakes": mistakes, "total": len(mistakes)}


def _card_payload(card: Flashcard, now: datetime) -> dict:
    return {
        "id": card.id,
        "front": card.front,
        "back": card.back,
        "category": card.category,
        "leitner_box": card.leitner_box,
        "due_at": card.due_at.isoformat(),
        "is_due": card.due_at <= now,
        "source_question_id": card.source_question_id,
    }
