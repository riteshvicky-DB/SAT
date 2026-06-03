"""
One-time script: scramble correct answer positions for all questions in the DB.
For each question, randomly reassign which choice (A/B/C/D) holds the correct answer.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal, init_db
from app.models import Question


def scramble() -> None:
    init_db()
    db = SessionLocal()
    try:
        questions = db.query(Question).all()
        print(f"Scrambling {len(questions)} questions...")

        for q in questions:
            choices = json.loads(q.choices_json or "[]")
            if len(choices) < 2:
                continue

            # Find the current correct choice object
            correct_obj = next((c for c in choices if c["id"] == q.correct_answer), None)
            if correct_obj is None:
                continue

            # Shuffle choices and reassign A/B/C/D labels
            rng = random.Random(q.id * 7919)   # deterministic per question
            labels = ["A", "B", "C", "D"][: len(choices)]
            texts = [c["text"] for c in choices]
            rng.shuffle(texts)

            new_choices = [{"id": lbl, "text": txt} for lbl, txt in zip(labels, texts)]
            # Find where the correct text landed
            correct_text = correct_obj["text"]
            new_correct = next(c["id"] for c in new_choices if c["text"] == correct_text)

            q.choices_json = json.dumps(new_choices)
            q.correct_answer = new_correct

        db.commit()

        # Verify distribution
        from sqlalchemy import func, select
        rows = db.execute(
            select(Question.correct_answer, func.count()).group_by(Question.correct_answer)
        ).all()
        print("New answer distribution:", dict(rows))
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    scramble()
