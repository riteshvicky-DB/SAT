from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import AiChatRequest
from app.services.ai_service import LocalAiService, tutor_system_prompt

router = APIRouter(prefix="/ai", tags=["ai"])
ai = LocalAiService()


class LlmSettingsRequest(BaseModel):
    provider: str          # "local" | "claude" | "openai" | "gemini"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    local_model: str = ""  # specific local model to pin


@router.get("/status")
async def status() -> dict:
    return await ai.status()


@router.post("/settings")
async def update_llm_settings(
    body: LlmSettingsRequest,
    _user: User = Depends(get_current_user),
) -> dict:
    """Persist LLM provider + API keys. Sets os.environ immediately (in-process)
    and writes to backend/.env for persistence across restarts."""
    import os as _os
    from fastapi import HTTPException

    valid = {"local", "claude", "openai", "gemini"}
    if body.provider not in valid:
        raise HTTPException(status_code=400, detail=f"provider must be one of {valid}")

    # ── 1. Set os.environ immediately so the running process picks it up ──────
    _os.environ["SAT_ACTIVE_LLM_PROVIDER"] = body.provider
    if body.anthropic_api_key:
        _os.environ["SAT_ANTHROPIC_API_KEY"] = body.anthropic_api_key
    if body.openai_api_key:
        _os.environ["SAT_OPENAI_API_KEY"] = body.openai_api_key
    if body.gemini_api_key:
        _os.environ["SAT_GEMINI_API_KEY"] = body.gemini_api_key
    if body.local_model:
        _os.environ["SAT_ACTIVE_LOCAL_MODEL"] = body.local_model

    # ── 2. Persist to .env file ───────────────────────────────────────────────
    env_data = {
        "SAT_ACTIVE_LLM_PROVIDER": body.provider,
        "SAT_ANTHROPIC_API_KEY": body.anthropic_api_key,
        "SAT_OPENAI_API_KEY": body.openai_api_key,
        "SAT_GEMINI_API_KEY": body.gemini_api_key,
        "SAT_ACTIVE_LOCAL_MODEL": body.local_model,
    }
    for candidate in ["backend/.env", ".env"]:
        if _os.path.isdir(_os.path.dirname(_os.path.abspath(candidate)) if _os.path.dirname(candidate) else "."):
            _write_env(candidate, env_data)
            break

    # ── 3. Reload settings from fresh env so next request uses new values ─────
    get_settings.cache_clear()
    new_settings = get_settings()
    ai.settings = new_settings

    return {
        "message": "LLM settings saved",
        "provider": body.provider,
        "active_provider": new_settings.active_llm_provider,
    }


@router.post("/eject")
async def eject_local_model(
    _user: User = Depends(get_current_user),
) -> dict:
    """Eject (deselect) the pinned local model — falls back to auto-pick."""
    import os as _os
    _os.environ.pop("SAT_ACTIVE_LOCAL_MODEL", None)
    _os.environ["SAT_ACTIVE_LLM_PROVIDER"] = "local"
    for candidate in ["backend/.env", ".env"]:
        if _os.path.exists(candidate):
            _write_env(candidate, {"SAT_ACTIVE_LOCAL_MODEL": "", "SAT_ACTIVE_LLM_PROVIDER": "local"})
            break
    get_settings.cache_clear()
    ai.settings = get_settings()
    return {"message": "Model ejected. Auto-selecting best available local model."}


class LoadModelRequest(BaseModel):
    model: str


@router.post("/load-local-model")
async def load_local_model(
    body: LoadModelRequest,
    _user: User = Depends(get_current_user),
) -> dict:
    """Unload current LM Studio model(s) and load the requested one."""
    from fastapi import HTTPException
    try:
        result = await ai.lm_studio_switch_model(body.model)
        # Pin this model as active in settings
        import os as _os
        _os.environ["SAT_ACTIVE_LOCAL_MODEL"] = body.model
        _os.environ["SAT_ACTIVE_LLM_PROVIDER"] = "local"
        get_settings.cache_clear()
        ai.settings = get_settings()
        return {"status": "ok", "model": body.model, "detail": result}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/chat")
async def chat(request: AiChatRequest) -> dict:
    messages = [
        {"role": "system", "content": tutor_system_prompt()},
        {"role": "user", "content": _compose_user_message(request)},
    ]
    content = await ai.complete(request.task, messages)
    return {"content": content}


@router.post("/chat/stream")
async def stream_chat(request: AiChatRequest) -> StreamingResponse:
    messages = [
        {"role": "system", "content": tutor_system_prompt()},
        {"role": "user", "content": _compose_user_message(request)},
    ]

    async def events():
        async for token in ai.stream(request.task, messages):
            yield f"data: {token}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


def _compose_user_message(request: AiChatRequest) -> str:
    if request.context:
        return f"Context:\n{request.context}\n\nStudent question:\n{request.message}"
    return request.message


def _write_env(path: str, values: dict[str, str]) -> None:
    """Update or create .env file with given key=value pairs."""
    import os
    lines: list[str] = []
    if os.path.exists(path):
        with open(path) as f:
            lines = f.readlines()
    updated_keys: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        key = line.split("=")[0].strip()
        if key in values:
            if values[key]:  # only write non-empty
                new_lines.append(f"{key}={values[key]}\n")
            updated_keys.add(key)
        else:
            new_lines.append(line)
    for key, val in values.items():
        if key not in updated_keys and val:
            new_lines.append(f"{key}={val}\n")
    with open(path, "w") as f:
        f.writelines(new_lines)
