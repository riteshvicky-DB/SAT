from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.config import get_settings
from app.core.database import engine, init_db
from app.routers import admin, ai, analytics, auth, flashcards, practice, study, tests

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


def _migrate_users_table() -> None:
    """Add new auth columns to existing users table without dropping data."""
    inspector = inspect(engine)
    existing = {col["name"] for col in inspector.get_columns("users")}
    new_cols = {
        "email": "VARCHAR(255)",
        "hashed_password": "VARCHAR(255)",
        "google_id": "VARCHAR(120)",
        "role": "VARCHAR(20) DEFAULT 'user'",
        "is_active": "BOOLEAN DEFAULT 1",
        "last_login": "DATETIME",
    }
    with engine.begin() as conn:
        for col, definition in new_cols.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {definition}"))


@app.on_event("startup")
def startup() -> None:
    init_db()
    _migrate_users_table()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/curriculum")
def curriculum() -> dict:
    from app.services.curriculum import SAT_CURRICULUM
    return SAT_CURRICULUM


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(ai.router)
app.include_router(practice.router)
app.include_router(analytics.router)
app.include_router(flashcards.router)
app.include_router(study.router)
app.include_router(tests.router)
