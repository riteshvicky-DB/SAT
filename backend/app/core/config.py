from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Offline SAT Academy"
    db_path: str = "data/sat_academy.sqlite3"
    lm_studio_base_url: str = "http://localhost:1234/v1"
    ollama_base_url: str = "http://localhost:11434"
    encryption_key: str = "local-dev-key-change-me"
    cors_origins: list[str] = ["*"]  # open for local network access; restrict in production

    # JWT
    secret_key: str = "sat-academy-secret-change-in-production-2024"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # SMTP (Gmail)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "satmasterai@gmail.com"
    smtp_pass: str = "eprl kqth jdxr kphc"
    smtp_from: str = "SAT Academy <satmasterai@gmail.com>"

    # Google OAuth (optional — app works fully offline without it)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    frontend_url: str = "http://localhost:5173"

    # Password reset token expiry (minutes)
    reset_token_expire_minutes: int = 30

    # External AI API keys (optional — app works fully offline without them)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    # Active LLM provider: "local" | "claude" | "openai" | "gemini"
    active_llm_provider: str = "local"
    # Which local model to use (empty = auto-pick best available)
    active_local_model: str = ""

    model_config = SettingsConfigDict(
        env_prefix="SAT_",
        env_file=["backend/.env", ".env"],   # check both locations
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
