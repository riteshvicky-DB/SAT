from math import exp

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Answer, Question, Weakness


def estimate_scores(db: Session, user_id: int) -> dict:
    rows = db.execute(
        select(Answer, Question).join(Question, Question.id == Answer.question_id).where(Answer.user_id == user_id)
    ).all()
    if not rows:
        return _empty_score()

    section_stats = {
        "math": {"weighted": 0.0, "possible": 0.0},
        "reading_writing": {"weighted": 0.0, "possible": 0.0},
    }
    weights = {"easy": 0.8, "medium": 1.0, "hard": 1.25, "sat_hard": 1.45}
    for answer, question in rows:
        weight = weights.get(question.difficulty, 1.0)
        section_stats[question.section]["possible"] += weight
        section_stats[question.section]["weighted"] += weight if answer.is_correct else 0.0

    math = _section_score(section_stats["math"])
    rw = _section_score(section_stats["reading_writing"])
    total = math + rw
    return {
        "total": total,
        "math": math,
        "reading_writing": rw,
        "percentile": _percentile(total),
        "probabilities": {
            "1200": _probability(total, 1200),
            "1300": _probability(total, 1300),
            "1400": _probability(total, 1400),
            "1500+": _probability(total, 1500),
            "1550+": _probability(total, 1550),
        },
    }


def mastery_summary(db: Session, user_id: int) -> list[dict]:
    weaknesses = db.execute(select(Weakness).where(Weakness.user_id == user_id).order_by(Weakness.mastery.asc())).scalars().all()
    return [
        {
            "section": item.section,
            "domain": item.domain,
            "skill": item.skill,
            "slug": item.slug,
            "mastery": round(item.mastery, 3),
            "attempts": item.attempts,
            "misses": item.misses,
            "remediation_unlocked": item.remediation_unlocked,
        }
        for item in weaknesses
    ]


def _section_score(stats: dict[str, float]) -> int:
    if stats["possible"] == 0:
        return 400
    accuracy = stats["weighted"] / stats["possible"]
    scaled = 200 + round(600 * accuracy)
    return max(200, min(800, scaled))


def _probability(score: int, target: int) -> float:
    return round(1 / (1 + exp(-(score - target) / 55)), 3)


def _percentile(score: int) -> int:
    bands = [(1550, 99), (1500, 98), (1450, 96), (1400, 93), (1350, 90), (1300, 86), (1200, 75), (1100, 61)]
    for threshold, percentile in bands:
        if score >= threshold:
            return percentile
    return max(1, min(60, round((score - 400) / 700 * 60)))


def _empty_score() -> dict:
    return {
        "total": 800,
        "math": 400,
        "reading_writing": 400,
        "percentile": 25,
        "probabilities": {"1200": 0.0, "1300": 0.0, "1400": 0.0, "1500+": 0.0, "1550+": 0.0},
    }
