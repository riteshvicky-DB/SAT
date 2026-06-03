from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Section(str, Enum):
    math = "math"
    reading_writing = "reading_writing"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    sat_hard = "sat_hard"


class QuestionType(str, Enum):
    multiple_choice = "multiple_choice"
    numeric_response = "numeric_response"
    passage_based = "passage_based"
    graph_interpretation = "graph_interpretation"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Student")
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="user")  # "user" | "admin"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    target_score: Mapped[int] = mapped_column(Integer, default=1500)
    study_minutes_per_day: Mapped[int] = mapped_column(Integer, default=60)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    answers: Mapped[list["Answer"]] = relationship(back_populates="user")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    section: Mapped[str] = mapped_column(String(40), index=True)
    domain: Mapped[str] = mapped_column(String(120), index=True)
    skill: Mapped[str] = mapped_column(String(160), index=True)
    difficulty: Mapped[str] = mapped_column(String(40), index=True)
    question_type: Mapped[str] = mapped_column(String(60))
    prompt: Mapped[str] = mapped_column(Text)
    passage: Mapped[str | None] = mapped_column(Text, nullable=True)
    choices_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(240))
    explanation: Mapped[str] = mapped_column(Text)
    distractor_analysis_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    graph_svg: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_seconds: Mapped[int] = mapped_column(Integer, default=75)
    created_by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class PracticeTest(Base):
    __tablename__ = "practice_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    is_full_length: Mapped[bool] = mapped_column(Boolean, default=False)
    module_plan_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    test_id: Mapped[int | None] = mapped_column(ForeignKey("practice_tests.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(60), default="practice")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    predicted_score: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("test_sessions.id"), nullable=True)
    selected_answer: Mapped[str] = mapped_column(String(240))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[int] = mapped_column(Integer, default=3)
    seconds_spent: Mapped[int] = mapped_column(Integer, default=0)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    user: Mapped[User] = relationship(back_populates="answers")


class Weakness(Base):
    __tablename__ = "weaknesses"
    __table_args__ = (UniqueConstraint("user_id", "skill", name="uq_weakness_user_skill"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    section: Mapped[str] = mapped_column(String(40))
    domain: Mapped[str] = mapped_column(String(120))
    skill: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), index=True)
    mastery: Mapped[float] = mapped_column(Float, default=0.0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    misses: Mapped[int] = mapped_column(Integer, default=0)
    remediation_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), default="mistake")
    leitner_box: Mapped[int] = mapped_column(Integer, default=1)
    due_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    source_question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id"), nullable=True)


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class VideoRecommendation(Base):
    __tablename__ = "video_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill: Mapped[str] = mapped_column(String(160), index=True)
    provider: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(240))
    url: Mapped[str] = mapped_column(String(500))
    timestamp_seconds: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")


class AiCache(Base):
    __tablename__ = "ai_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    task: Mapped[str] = mapped_column(String(80))
    response_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
