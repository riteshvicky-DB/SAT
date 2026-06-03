import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator

class _Email(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

EmailStr = str  # use plain str with manual validation below
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models import PasswordResetToken, User
from app.services.email import send_reset_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ── Schemas ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    target_score: int | None = None
    study_minutes_per_day: int | None = None


# ── Helpers ────────────────────────────────────────────────────────────────────

def _user_payload(user: User, token: str) -> dict:
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "target_score": user.target_score,
            "study_minutes_per_day": user.study_minutes_per_day,
            "xp": user.xp,
            "streak_days": user.streak_days,
        },
    }


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    if db.execute(select(User).where(User.email == body.email)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    background.add_task(send_welcome_email, user.email, user.name)
    token = create_access_token(user.id, user.role)
    return _user_payload(user, token)


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
    if user is None or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    user.last_login = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    token = create_access_token(user.id, user.role)
    return _user_payload(user, token)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "target_score": current_user.target_score,
        "study_minutes_per_day": current_user.study_minutes_per_day,
        "xp": current_user.xp,
        "streak_days": current_user.streak_days,
        "created_at": current_user.created_at.isoformat(),
    }


@router.patch("/me")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if body.name is not None:
        current_user.name = body.name
    if body.target_score is not None:
        current_user.target_score = body.target_score
    if body.study_minutes_per_day is not None:
        current_user.study_minutes_per_day = body.study_minutes_per_day
    db.commit()
    return {"message": "Profile updated"}


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
    # Always return success to prevent email enumeration
    if user and user.hashed_password:
        token_str = secrets.token_urlsafe(32)
        expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            minutes=settings.reset_token_expire_minutes
        )
        db.add(PasswordResetToken(user_id=user.id, token=token_str, expires_at=expires))
        db.commit()
        reset_url = f"{settings.frontend_url}/reset-password?token={token_str}"
        background.add_task(send_reset_email, user.email, reset_url, user.name)
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    record = db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == body.token)
    ).scalar_one_or_none()
    if record is None or record.used:
        raise HTTPException(status_code=400, detail="Invalid or already-used reset token")
    if record.expires_at < datetime.now(UTC).replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    user = db.get(User, record.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(body.new_password)
    record.used = True
    db.commit()
    return {"message": "Password reset successfully. You can now log in."}


# ── Google OAuth ───────────────────────────────────────────────────────────────

@router.get("/google")
def google_login() -> dict:
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    from urllib.parse import urlencode
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"url": url}


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    import httpx
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        google_user = user_resp.json()

    email = google_user.get("email")
    google_id = google_user.get("sub")
    name = google_user.get("name", "Student")

    # Find or create user
    user = db.execute(select(User).where(User.google_id == google_id)).scalar_one_or_none()
    if user is None:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        user = User(name=name, email=email, google_id=google_id, role="user")
        db.add(user)
    else:
        user.google_id = google_id
    user.last_login = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    return RedirectResponse(f"{settings.frontend_url}?token={token}")
