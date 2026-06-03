import json
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Answer, PracticeTest, Question, TestSession, User
from app.services.adaptive import question_to_payload

router = APIRouter(prefix="/tests", tags=["tests"])

# Real Digital SAT structure
SAT_MODULES = {
    "math": [
        {"module": 1, "minutes": 35, "count": 22},
        {"module": 2, "minutes": 35, "count": 22},
    ],
    "reading_writing": [
        {"module": 1, "minutes": 32, "count": 27},
        {"module": 2, "minutes": 32, "count": 27},
    ],
}

TOTAL_MODELS = 100

# Cache the shuffled ID order per section so we only compute it once per process.
_SHUFFLED_IDS: dict[str, list[int]] = {}


def _get_shuffled_ids(db: Session, section: str) -> list[int]:
    """
    Return all question IDs for a section in a stable shuffled order.
    Shuffled once with a fixed seed so every call returns identical ordering,
    but skills are fully interleaved instead of grouped by insertion order.
    Cached in memory after the first call.
    """
    if section not in _SHUFFLED_IDS:
        ids = db.execute(
            select(Question.id).where(Question.section == section).order_by(Question.id)
        ).scalars().all()
        shuffled = list(ids)
        random.Random(42).shuffle(shuffled)
        _SHUFFLED_IDS[section] = shuffled
    return _SHUFFLED_IDS[section]


def _questions_for_model(db: Session, section: str, model_number: int) -> list[list[Question]]:
    """
    Return deterministic, non-overlapping question sets for each module.
    Uses a fixed global shuffle of all IDs so every model gets a balanced
    mix of skills/topics instead of a block from one skill.
    """
    specs = SAT_MODULES[section]
    per_model = sum(s["count"] for s in specs)
    offset = (model_number - 1) * per_model

    all_ids = _get_shuffled_ids(db, section)
    model_ids = all_ids[offset: offset + per_model]

    # Fetch full question objects and restore shuffled order
    rows_by_id = {
        q.id: q for q in db.execute(
            select(Question).where(Question.id.in_(model_ids))
        ).scalars().all()
    }
    rows = [rows_by_id[qid] for qid in model_ids if qid in rows_by_id]

    # Split into modules
    modules = []
    pos = 0
    for spec in specs:
        modules.append(rows[pos: pos + spec["count"]])
        pos += spec["count"]
    return modules


@router.get("/models/{section}")
def list_models(section: str, db: Session = Depends(get_db)) -> dict:
    """Return metadata for all 100 test models for a section."""
    if section not in SAT_MODULES:
        raise HTTPException(status_code=400, detail=f"Unknown section '{section}'.")
    specs = SAT_MODULES[section]
    total_q = sum(s["count"] for s in specs)
    available = db.execute(
        select(func.count()).select_from(Question).where(Question.section == section)
    ).scalar_one()
    max_models = min(TOTAL_MODELS, available // total_q)
    return {
        "section": section,
        "total_models": max_models,
        "questions_per_model": total_q,
        "modules": specs,
    }


@router.get("/section/{section}/{model_number}")
def get_model_test(section: str, model_number: int, db: Session = Depends(get_db)) -> dict:
    """Return a specific numbered test model (1-100) with non-repeating questions."""
    if section not in SAT_MODULES:
        raise HTTPException(status_code=400, detail=f"Unknown section '{section}'.")
    if model_number < 1 or model_number > TOTAL_MODELS:
        raise HTTPException(status_code=400, detail=f"Model number must be between 1 and {TOTAL_MODELS}.")

    specs = SAT_MODULES[section]
    question_modules = _questions_for_model(db, section, model_number)

    payload_modules = []
    for spec, questions in zip(specs, question_modules):
        payload_modules.append({
            "section": section,
            "module": spec["module"],
            "minutes": spec["minutes"],
            "questions": spec["count"],
            "items": [question_to_payload(q) for q in questions],
        })

    title = "Math" if section == "math" else "Reading & Writing"
    return {
        "title": f"Digital SAT — {title} · Model {model_number}",
        "section": section,
        "model_number": model_number,
        "modules": payload_modules,
    }


@router.get("/section/{section}")
def section_test(section: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return get_model_test(section, 1, db)


@router.get("/bluebook-simulation")
def bluebook_simulation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    all_modules = []
    for section in ("reading_writing", "math"):
        specs = SAT_MODULES[section]
        question_modules = _questions_for_model(db, section, 1)
        for spec, questions in zip(specs, question_modules):
            all_modules.append({
                "section": section, "module": spec["module"], "minutes": spec["minutes"],
                "questions": spec["count"], "items": [question_to_payload(q) for q in questions],
            })
        if section == "reading_writing":
            all_modules.append({"section": "break", "module": 0, "minutes": 10, "questions": 0, "items": []})
    return {"title": "Digital SAT Full-Length Simulation", "modules": all_modules}


@router.post("/session")
def create_session(
    mode: str = "full_test",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    test = PracticeTest(title="Digital SAT Simulation", is_full_length=True, module_plan_json=json.dumps({}))
    db.add(test)
    db.flush()
    session = TestSession(user_id=current_user.id, test_id=test.id, mode=mode)
    db.add(session)
    db.commit()
    return {"session_id": session.id, "test_id": test.id}
