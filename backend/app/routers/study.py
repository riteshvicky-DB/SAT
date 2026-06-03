import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import StudyPlan, User
from app.schemas import StudyPlanRequest
from app.services.scoring import mastery_summary

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/plan")
def create_study_plan(
    request: StudyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    weak = mastery_summary(db, current_user.id)[:6]
    daily_blocks = []
    for day in range(1, request.days + 1):
        focus = weak[(day - 1) % len(weak)] if weak else {"skill": "Diagnostic practice", "domain": "Mixed SAT"}
        daily_blocks.append({
            "day": day,
            "minutes": request.minutes_per_day,
            "focus": focus["skill"],
            "schedule": [
                {"activity": "Warm-up review", "minutes": 10},
                {"activity": f"Adaptive practice: {focus['skill']}", "minutes": max(20, request.minutes_per_day - 30)},
                {"activity": "Mistake journal and flashcards", "minutes": 15},
                {"activity": "AI tutor remediation", "minutes": 5},
            ],
        })
    plan = {
        "target_score": request.target_score,
        "created_at": datetime.now(UTC).isoformat(),
        "weekly_targets": ["Raise weakest topic mastery above 70%", "Keep daily streak", "Complete one timed module"],
        "days": daily_blocks,
    }
    db.add(StudyPlan(user_id=current_user.id, plan_json=json.dumps(plan)))
    db.commit()
    return plan
