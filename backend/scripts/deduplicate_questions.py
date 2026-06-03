"""Remove duplicate questions keeping the one with the lowest id per unique (section, prompt, passage) combo."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal, init_db
from app.models import Question
from sqlalchemy import select, func, delete


def deduplicate() -> None:
    init_db()
    db = SessionLocal()
    try:
        before = db.query(Question).count()

        # For math: unique by (prompt) — keep lowest id
        math_dups = db.execute(
            select(Question.prompt, func.min(Question.id).label("keep_id"))
            .where(Question.section == "math")
            .group_by(Question.prompt)
            .having(func.count() > 1)
        ).all()

        math_removed = 0
        for prompt, keep_id in math_dups:
            ids_to_delete = db.execute(
                select(Question.id)
                .where(Question.section == "math", Question.prompt == prompt, Question.id != keep_id)
            ).scalars().all()
            for qid in ids_to_delete:
                db.execute(delete(Question).where(Question.id == qid))
                math_removed += 1

        # For RW: unique by (prompt, passage) — keep lowest id
        rw_dups = db.execute(
            select(Question.prompt, Question.passage, func.min(Question.id).label("keep_id"))
            .where(Question.section == "reading_writing")
            .group_by(Question.prompt, Question.passage)
            .having(func.count() > 1)
        ).all()

        rw_removed = 0
        for prompt, passage, keep_id in rw_dups:
            ids_to_delete = db.execute(
                select(Question.id)
                .where(
                    Question.section == "reading_writing",
                    Question.prompt == prompt,
                    Question.passage == passage,
                    Question.id != keep_id,
                )
            ).scalars().all()
            for qid in ids_to_delete:
                db.execute(delete(Question).where(Question.id == qid))
                rw_removed += 1

        db.commit()

        after = db.query(Question).count()
        math_after = db.query(Question).filter(Question.section == "math").count()
        rw_after = db.query(Question).filter(Question.section == "reading_writing").count()
        print(f"Removed {math_removed} math duplicates, {rw_removed} RW duplicates.")
        print(f"Before: {before} → After: {after} (math: {math_after}, rw: {rw_after})")

        # Verify
        remaining_math_dups = db.execute(
            select(func.count())
            .select_from(
                select(Question.prompt)
                .where(Question.section == "math")
                .group_by(Question.prompt)
                .having(func.count() > 1)
                .subquery()
            )
        ).scalar_one()
        print(f"Remaining math duplicate prompts: {remaining_math_dups} (should be 0)")

    finally:
        db.close()


if __name__ == "__main__":
    deduplicate()
