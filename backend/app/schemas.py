from pydantic import BaseModel, Field


class Choice(BaseModel):
    id: str
    text: str


class QuestionRead(BaseModel):
    id: int
    external_id: str
    section: str
    domain: str
    skill: str
    difficulty: str
    question_type: str
    prompt: str
    passage: str | None = None
    choices: list[Choice] = []
    graph_svg: str | None = None
    estimated_seconds: int


class AnswerCreate(BaseModel):
    user_id: int = 1
    question_id: int
    selected_answer: str
    session_id: int | None = None
    confidence: int = Field(default=3, ge=1, le=5)
    seconds_spent: int = Field(default=0, ge=0)
    flagged: bool = False


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    weakness_slug: str | None
    mastery: float
    ai_feedback: str | None = None


class AiChatRequest(BaseModel):
    user_id: int = 1
    message: str
    context: str | None = None
    task: str = "tutoring"
    stream: bool = False


class AiStatus(BaseModel):
    provider: str
    available: bool
    models: list[str]
    selected_reasoning_model: str
    selected_fast_model: str


class PracticeRequest(BaseModel):
    user_id: int = 1
    section: str | None = None
    domain: str | None = None
    skill: str | None = None
    count: int = Field(default=10, ge=1, le=50)


class StudyPlanRequest(BaseModel):
    user_id: int = 1
    target_score: int = Field(default=1500, ge=400, le=1600)
    minutes_per_day: int = Field(default=60, ge=10, le=480)
    days: int = Field(default=7, ge=1, le=90)
