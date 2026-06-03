from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Answer, Question, User
from app.schemas import AnswerCreate, PracticeRequest
from app.services.adaptive import question_to_payload, select_adaptive_questions, update_mastery
from app.services.spaced_repetition import create_mistake_flashcard
from app.services.video_map import get_video_url, is_search_url

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("/next")
def next_questions(
    request: PracticeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    questions = select_adaptive_questions(
        db=db,
        user_id=current_user.id,
        count=request.count,
        section=request.section,
        domain=request.domain,
        skill=request.skill,
    )
    return {"questions": [question_to_payload(q) for q in questions]}


@router.post("/answer")
def answer_question(
    request: AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    question = db.get(Question, request.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    normalized_selected = request.selected_answer.strip().lower()
    normalized_correct = question.correct_answer.strip().lower()
    is_correct = normalized_selected == normalized_correct
    answer = Answer(
        user_id=current_user.id,
        question_id=request.question_id,
        session_id=request.session_id,
        selected_answer=request.selected_answer,
        is_correct=is_correct,
        confidence=request.confidence,
        seconds_spent=request.seconds_spent,
        flagged=request.flagged,
    )
    db.add(answer)
    weakness = update_mastery(db, current_user.id, question, is_correct)
    if not is_correct:
        create_mistake_flashcard(db, current_user.id, question)
    db.commit()
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "weakness_slug": weakness.slug,
        "mastery": round(weakness.mastery, 3),
        "remediation_unlocked": weakness.remediation_unlocked,
        "video_url": get_video_url(question.skill, question.section) if not is_correct else None,
        "video_label": ("Search SAT Tutorial" if is_search_url(get_video_url(question.skill, question.section)) else "Watch SAT Tutorial") if not is_correct else None,
        "skill": question.skill,
        "section": question.section,
    }


@router.get("/weakness/{slug}")
def weakness_lab(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    questions = db.execute(
        select(Question).where(Question.skill.ilike(f"%{slug.split('-')[-1]}%")).limit(30)
    ).scalars().all()
    return {"slug": slug, "questions": [question_to_payload(q) for q in questions]}
