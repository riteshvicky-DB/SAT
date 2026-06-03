from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Answer, Flashcard, Question, User, Weakness

router = APIRouter(prefix="/admin", tags=["admin"])


class UserUpdateRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    name: str | None = None


@router.get("/users")
def list_users(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    users = db.execute(select(User).order_by(User.created_at.desc())).scalars().all()
    result = []
    for u in users:
        attempts = db.execute(
            select(func.count()).select_from(Answer).where(Answer.user_id == u.id)
        ).scalar_one()
        correct = db.execute(
            select(func.count()).select_from(Answer)
            .where(Answer.user_id == u.id, Answer.is_correct.is_(True))
        ).scalar_one()
        # Estimated scores from weaknesses
        weaknesses = db.execute(
            select(Weakness).where(Weakness.user_id == u.id)
        ).scalars().all()
        math_mastery = _section_mastery(weaknesses, "math")
        rw_mastery = _section_mastery(weaknesses, "reading_writing")
        math_score = _mastery_to_score(math_mastery)
        rw_score = _mastery_to_score(rw_mastery)
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "target_score": u.target_score,
            "xp": u.xp,
            "streak_days": u.streak_days,
            "attempts": attempts,
            "accuracy": round(correct / attempts, 3) if attempts else 0,
            "estimated_total": math_score + rw_score,
            "estimated_math": math_score,
            "estimated_rw": rw_score,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "created_at": u.created_at.isoformat(),
        })
    return {"users": result, "total": len(result)}


@router.get("/users/{user_id}")
def user_detail(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Answers summary
    total = db.execute(
        select(func.count()).select_from(Answer).where(Answer.user_id == user_id)
    ).scalar_one()
    correct = db.execute(
        select(func.count()).select_from(Answer)
        .where(Answer.user_id == user_id, Answer.is_correct.is_(True))
    ).scalar_one()
    avg_secs = db.execute(
        select(func.avg(Answer.seconds_spent)).where(Answer.user_id == user_id)
    ).scalar_one() or 0

    # Section breakdown
    math_total = db.execute(
        select(func.count()).select_from(Answer)
        .join(Question, Answer.question_id == Question.id)
        .where(Answer.user_id == user_id, Question.section == "math")
    ).scalar_one()
    math_correct = db.execute(
        select(func.count()).select_from(Answer)
        .join(Question, Answer.question_id == Question.id)
        .where(Answer.user_id == user_id, Question.section == "math", Answer.is_correct.is_(True))
    ).scalar_one()
    rw_total = total - math_total
    rw_correct = correct - math_correct

    # Weaknesses / mastery
    weaknesses = db.execute(
        select(Weakness).where(Weakness.user_id == user_id).order_by(Weakness.mastery.asc())
    ).scalars().all()
    math_mastery = _section_mastery(weaknesses, "math")
    rw_mastery = _section_mastery(weaknesses, "reading_writing")

    # Skill breakdown
    skill_rows = []
    for w in sorted(weaknesses, key=lambda x: x.mastery):
        skill_rows.append({
            "section": w.section,
            "domain": w.domain,
            "skill": w.skill,
            "mastery": round(w.mastery, 3),
            "attempts": w.attempts or 0,
            "misses": w.misses or 0,
            "accuracy": round(1 - (w.misses or 0) / max(w.attempts or 1, 1), 3),
            "remediation_unlocked": w.remediation_unlocked,
        })

    # Daily activity (last 30 days)
    since = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30)
    daily_rows = db.execute(
        select(Answer.answered_at, Answer.is_correct, Answer.seconds_spent)
        .where(Answer.user_id == user_id, Answer.answered_at >= since)
        .order_by(Answer.answered_at)
    ).all()
    daily: dict[str, dict] = {}
    for answered_at, is_correct, secs in daily_rows:
        key = answered_at.date().isoformat()
        b = daily.setdefault(key, {"date": key, "attempts": 0, "correct": 0, "seconds": 0})
        b["attempts"] += 1
        b["correct"] += 1 if is_correct else 0
        b["seconds"] += secs
    activity = [
        {**b,
         "accuracy": round(b["correct"] / b["attempts"], 3) if b["attempts"] else 0,
         "avg_seconds": round(b["seconds"] / b["attempts"], 1) if b["attempts"] else 0}
        for b in daily.values()
    ]

    # Recent wrong answers
    mistakes = db.execute(
        select(Answer, Question)
        .join(Question, Answer.question_id == Question.id)
        .where(Answer.user_id == user_id, Answer.is_correct.is_(False))
        .order_by(Answer.answered_at.desc())
        .limit(10)
    ).all()

    # Flashcards
    fc_total = db.execute(
        select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id)
    ).scalar_one()
    fc_due = db.execute(
        select(func.count()).select_from(Flashcard)
        .where(Flashcard.user_id == user_id,
               Flashcard.due_at <= datetime.now(UTC).replace(tzinfo=None))
    ).scalar_one()

    return {
        "user": {
            "id": user.id, "name": user.name, "email": user.email,
            "role": user.role, "is_active": user.is_active,
            "target_score": user.target_score,
            "study_minutes_per_day": user.study_minutes_per_day,
            "xp": user.xp, "streak_days": user.streak_days,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat(),
        },
        "performance": {
            "total_attempts": total,
            "total_correct": correct,
            "overall_accuracy": round(correct / total, 3) if total else 0,
            "avg_seconds_per_question": round(avg_secs, 1),
            "math": {
                "attempts": math_total, "correct": math_correct,
                "accuracy": round(math_correct / math_total, 3) if math_total else 0,
                "mastery": round(math_mastery, 3),
                "estimated_score": _mastery_to_score(math_mastery),
            },
            "reading_writing": {
                "attempts": rw_total, "correct": rw_correct,
                "accuracy": round(rw_correct / rw_total, 3) if rw_total else 0,
                "mastery": round(rw_mastery, 3),
                "estimated_score": _mastery_to_score(rw_mastery),
            },
            "estimated_total_score": _mastery_to_score(math_mastery) + _mastery_to_score(rw_mastery),
        },
        "skills": skill_rows,
        "activity": activity,
        "flashcards": {"total": fc_total, "due": fc_due},
        "recent_mistakes": [
            {
                "skill": q.skill, "difficulty": q.difficulty,
                "prompt": q.prompt[:100],
                "selected": a.selected_answer,
                "correct": q.correct_answer,
                "answered_at": a.answered_at.isoformat(),
            }
            for a, q in mistakes
        ],
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Delete related data first
    from sqlalchemy import delete as sql_delete
    from app.models import Answer, Flashcard, Weakness
    db.execute(sql_delete(Flashcard).where(Flashcard.user_id == user_id))
    db.execute(sql_delete(Answer).where(Answer.user_id == user_id))
    db.execute(sql_delete(Weakness).where(Weakness.user_id == user_id))
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    body: UserUpdateRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.name is not None:
        user.name = body.name
    db.commit()
    return {"message": "User updated"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _section_mastery(weaknesses: list, section: str) -> float:
    rows = [w.mastery for w in weaknesses if w.section == section]
    return sum(rows) / len(rows) if rows else 0.5


def _mastery_to_score(mastery: float) -> int:
    """Convert 0–1 mastery to approximate SAT section score (200–800)."""
    return round(200 + mastery * 600 / 10) * 10
