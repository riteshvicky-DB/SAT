import json

from sqlalchemy.orm import Session

from app.models import Question
from app.services.ai_service import LocalAiService, tutor_system_prompt


class QuestionGenerationService:
    def __init__(self) -> None:
        self.ai = LocalAiService()

    async def generate_reinforcement_set(
        self,
        db: Session,
        section: str,
        domain: str,
        skill: str,
        count: int = 30,
    ) -> list[Question]:
        prompt = (
            f"Generate {count} unique Digital SAT-style questions for {section}/{domain}/{skill}. "
            "Increase difficulty gradually. Return strict JSON array with fields: prompt, choices, "
            "correct_answer, explanation, difficulty, question_type, distractor_analysis."
        )
        content = await self.ai.complete(
            "question_generation",
            [{"role": "system", "content": tutor_system_prompt()}, {"role": "user", "content": prompt}],
        )
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = []

        questions: list[Question] = []
        for index, item in enumerate(data[:count]):
            question = Question(
                external_id=f"ai-{section}-{domain}-{skill}-{index}-{abs(hash(item.get('prompt', '')))}",
                section=section,
                domain=domain,
                skill=skill,
                difficulty=item.get("difficulty", "medium"),
                question_type=item.get("question_type", "multiple_choice"),
                prompt=item.get("prompt", ""),
                choices_json=json.dumps(item.get("choices", [])),
                correct_answer=str(item.get("correct_answer", "")),
                explanation=item.get("explanation", ""),
                distractor_analysis_json=json.dumps(item.get("distractor_analysis", {})),
                created_by_ai=True,
            )
            db.add(question)
            questions.append(question)
        db.flush()
        return questions
