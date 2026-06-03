import json
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Answer, Question, Weakness
from app.services.curriculum import slug_for_skill


DIFFICULTY_ORDER = ["easy", "medium", "hard", "sat_hard"]


def select_adaptive_questions(
    db: Session,
    user_id: int,
    count: int,
    section: str | None = None,
    domain: str | None = None,
    skill: str | None = None,
) -> list[Question]:
    weak_skills = db.execute(
        select(Weakness.skill).where(Weakness.user_id == user_id).order_by(Weakness.mastery.asc()).limit(5)
    ).scalars().all()

    answered_ids = set(
        db.execute(select(Answer.question_id).where(Answer.user_id == user_id).order_by(Answer.answered_at.desc()).limit(80))
        .scalars()
        .all()
    )

    query = select(Question)
    if section:
        query = query.where(Question.section == section)
    if domain:
        query = query.where(Question.domain == domain)
    if skill:
        query = query.where(Question.skill == skill)
    elif weak_skills:
        query = query.where(Question.skill.in_(weak_skills))

    candidates = [q for q in db.execute(query.order_by(func.random()).limit(count * 4)).scalars().all() if q.id not in answered_ids]
    if len(candidates) < count:
        candidate_ids = {q.id for q in candidates}
        excluded_ids = answered_ids | candidate_ids
        fallback_query = select(Question).where(Question.id.not_in(excluded_ids)) if excluded_ids else select(Question)
        fallback = db.execute(fallback_query.order_by(func.random()).limit(count - len(candidates))).scalars().all()
        candidates.extend(fallback)
    return candidates[:count]


def update_mastery(db: Session, user_id: int, question: Question, is_correct: bool) -> Weakness:
    slug = slug_for_skill(question.domain, question.skill)
    weakness = db.execute(
        select(Weakness).where(Weakness.user_id == user_id, Weakness.skill == question.skill)
    ).scalar_one_or_none()
    if weakness is None:
        weakness = Weakness(
            user_id=user_id,
            section=question.section,
            domain=question.domain,
            skill=question.skill,
            slug=slug,
            mastery=0.55,
        )
        db.add(weakness)

    weakness.attempts = (weakness.attempts or 0) + 1
    weakness.misses = (weakness.misses or 0) + (0 if is_correct else 1)
    delta = 0.08 if is_correct else -0.12
    speed_weight = 1.1 if question.difficulty in {"hard", "sat_hard"} and is_correct else 1.0
    weakness.mastery = max(0.0, min(1.0, weakness.mastery + delta * speed_weight))
    miss_rate = weakness.misses / max(weakness.attempts, 1)
    weakness.remediation_unlocked = weakness.attempts >= 5 and miss_rate > 0.8
    weakness.updated_at = datetime.now(UTC)
    db.flush()
    return weakness


def question_to_payload(question: Question) -> dict:
    return {
        "id": question.id,
        "external_id": question.external_id,
        "section": question.section,
        "domain": question.domain,
        "skill": question.skill,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "prompt": question.prompt,
        "passage": question.passage,
        "choices": json.loads(question.choices_json or "[]"),
        "graph_svg": question.graph_svg,
        "estimated_seconds": question.estimated_seconds,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "video_url": _video_url(question.skill, question.section),
    }


def _video_url(skill: str, section: str) -> str:
    from app.services.video_map import get_video_url
    return get_video_url(skill, section)
