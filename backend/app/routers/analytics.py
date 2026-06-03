from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Answer, Flashcard, Question, User, VideoRecommendation, Weakness
from app.services.scoring import estimate_scores, mastery_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user_id = current_user.id
    scores = estimate_scores(db, user_id)
    mastery = mastery_summary(db, user_id)
    attempts = db.execute(select(func.count()).select_from(Answer).where(Answer.user_id == user_id)).scalar_one()
    correct = db.execute(
        select(func.count()).select_from(Answer).where(Answer.user_id == user_id, Answer.is_correct.is_(True))
    ).scalar_one()
    due_cards = db.execute(
        select(func.count()).select_from(Flashcard).where(
            Flashcard.user_id == user_id,
            Flashcard.due_at <= datetime.now(UTC).replace(tzinfo=None),
        )
    ).scalar_one()
    return {
        "score": scores,
        "accuracy": round(correct / attempts, 3) if attempts else 0,
        "attempts": attempts,
        "due_flashcards": due_cards,
        "mastery": mastery,
        "trends": _daily_trends(db, user_id),
        "weakest": mastery[:5],
        "strongest": sorted(mastery, key=lambda r: r["mastery"], reverse=True)[:5],
    }


@router.get("/videos")
def videos(skill: str | None = None, db: Session = Depends(get_db)) -> dict:
    query = select(VideoRecommendation)
    if skill:
        query = query.where(VideoRecommendation.skill.ilike(f"%{skill}%"))
    rows = db.execute(query.limit(25)).scalars().all()
    return {
        "videos": [
            {"skill": r.skill, "provider": r.provider, "title": r.title,
             "url": r.url, "timestamp_seconds": r.timestamp_seconds, "notes": r.notes}
            for r in rows
        ]
    }


def _daily_trends(db: Session, user_id: int) -> list[dict]:
    since = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30)
    rows = db.execute(
        select(Answer.answered_at, Answer.is_correct, Answer.seconds_spent)
        .where(Answer.user_id == user_id, Answer.answered_at >= since)
        .order_by(Answer.answered_at)
    ).all()
    buckets: dict[str, dict] = {}
    for answered_at, is_correct, seconds_spent in rows:
        key = answered_at.date().isoformat()
        bucket = buckets.setdefault(key, {"date": key, "attempts": 0, "correct": 0, "seconds": 0})
        bucket["attempts"] += 1
        bucket["correct"] += 1 if is_correct else 0
        bucket["seconds"] += seconds_spent
    return [
        {**b, "accuracy": round(b["correct"] / b["attempts"], 3) if b["attempts"] else 0,
         "avg_seconds": round(b["seconds"] / b["attempts"], 1) if b["attempts"] else 0}
        for b in buckets.values()
    ]
