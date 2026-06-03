"""
Multi-provider AI service.
Supports: local (LM Studio / Ollama), Claude (Anthropic), OpenAI (GPT-4o), Google Gemini.
Falls back gracefully — if the selected provider is unavailable, returns a helpful message.
"""
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

REASONING_MODEL = "Qwen3 35B A3B"
FAST_MODELS = ["GPT-OSS 20B", "GLM 4.7 Flash"]
FALLBACK_MODEL = "Gemma 4 31B"


async def _complete_local(messages: list[dict], model: str, base_url: str) -> str:
    payload = {"model": model, "messages": messages, "temperature": 0.5, "stream": False}
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=300, write=30, pool=5)) as client:
        resp = await client.post(f"{base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _complete_claude(messages: list[dict], api_key: str) -> str:
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
    user_messages = [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"]
    payload: dict[str, Any] = {"model": "claude-opus-4-5", "max_tokens": 1024, "messages": user_messages}
    if system_msg:
        payload["system"] = system_msg
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


async def _complete_openai(messages: list[dict], api_key: str) -> str:
    payload = {"model": "gpt-4o", "messages": messages, "temperature": 0.5, "max_tokens": 1024}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _complete_gemini(messages: list[dict], api_key: str) -> str:
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    parts = []
    if system_msg:
        parts.append({"text": f"[System]: {system_msg}\n\n"})
    for m in messages:
        if m["role"] == "user":
            parts.append({"text": m["content"]})
        elif m["role"] == "assistant":
            parts.append({"text": f"[Assistant]: {m['content']}"})
    payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1024}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


class LocalAiService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def status(self) -> dict[str, Any]:
        s = get_settings()  # fresh read so UI always reflects current provider
        lm_models = await self._lm_studio_models()
        lm_model_states = await self._lm_studio_model_states() if lm_models else {}
        ollama_models = await self._ollama_models()
        local_models = lm_models or ollama_models
        best_local = self._best_available(local_models, [REASONING_MODEL, FALLBACK_MODEL]) if local_models else FALLBACK_MODEL
        pinned = s.active_local_model
        active_local = pinned if (pinned and pinned in local_models) else best_local
        return {
            "provider": s.active_llm_provider,
            "active_provider": s.active_llm_provider,
            "available": self._provider_available(s.active_llm_provider, local_models),
            "models": local_models,
            "model_states": lm_model_states,
            "selected_reasoning_model": active_local,
            "selected_fast_model": active_local,
            "active_local_model": active_local,
            "providers": {
                "local":  {"available": bool(local_models), "label": "Local LLM", "models": local_models, "model_states": lm_model_states},
                "claude": {"available": bool(s.anthropic_api_key), "label": "Claude (Anthropic)", "model": "claude-opus-4-5"},
                "openai": {"available": bool(s.openai_api_key),   "label": "ChatGPT (OpenAI)",    "model": "gpt-4o"},
                "gemini": {"available": bool(s.gemini_api_key),   "label": "Gemini (Google)",     "model": "gemini-2.0-flash"},
            },
        }

    def _provider_available(self, provider: str, local_models: list) -> bool:
        s = self.settings
        return {
            "local":  bool(local_models),
            "claude": bool(s.anthropic_api_key),
            "openai": bool(s.openai_api_key),
            "gemini": bool(s.gemini_api_key),
        }.get(provider, False)

    async def complete(self, task: str, messages: list[dict[str, str]], stream: bool = False) -> str:
        # Always read fresh settings so provider changes take effect immediately
        s = get_settings()
        p = s.active_llm_provider
        try:
            if p == "claude" and s.anthropic_api_key:
                return await _complete_claude(messages, s.anthropic_api_key)
            if p == "openai" and s.openai_api_key:
                return await _complete_openai(messages, s.openai_api_key)
            if p == "gemini" and s.gemini_api_key:
                return await _complete_gemini(messages, s.gemini_api_key)
            # Local fallback
            lm = await self._lm_studio_models()
            if lm:
                pinned = s.active_local_model
                model = pinned if pinned in lm else self._best_available(lm, [REASONING_MODEL, FALLBACK_MODEL])
                return await _complete_local(messages, model, s.lm_studio_base_url)
            ol = await self._ollama_models()
            if ol:
                pinned = s.active_local_model
                model = pinned if pinned in ol else ol[0]
                return await _complete_local(messages, model, f"{s.ollama_base_url}/v1")
            return "⚠️ No AI provider configured. Add an API key in Settings or start a local LLM."
        except Exception as exc:
            logger.error("AI completion failed (%s): %s", p, exc)
            return f"⚠️ AI error ({p}): {type(exc).__name__}: {_sanitize_error(str(exc))}"

    async def stream(self, task: str, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        content = await self.complete(task, messages)
        yield content

    async def _lm_studio_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(f"{self.settings.lm_studio_base_url}/models")
                resp.raise_for_status()
                return [item["id"] for item in resp.json().get("data", [])]
        except Exception:
            return []

    async def _lm_studio_model_states(self) -> dict[str, str]:
        """Returns {model_id: 'loaded'|'not-loaded'} from LM Studio /api/v0/models."""
        try:
            base = self.settings.lm_studio_base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(f"{base}/api/v0/models")
                resp.raise_for_status()
                return {item["id"]: item.get("state", "unknown") for item in resp.json().get("data", [])}
        except Exception:
            return {}

    async def lm_studio_switch_model(self, new_model: str) -> dict:
        """Unload currently loaded model(s) in LM Studio, then load the requested one."""
        base = self.settings.lm_studio_base_url.replace("/v1", "")
        async with httpx.AsyncClient(timeout=180) as client:
            # 1. Find loaded models and unload them
            states_resp = await client.get(f"{base}/api/v0/models")
            states_resp.raise_for_status()
            loaded = [m["id"] for m in states_resp.json().get("data", []) if m.get("state") == "loaded"]
            for mid in loaded:
                if mid != new_model:
                    await client.post(f"{base}/api/v1/models/unload",
                                      json={"instance_id": mid})

            # 2. Load the new model if not already loaded
            if new_model not in loaded:
                load_resp = await client.post(
                    f"{base}/api/v1/models/load",
                    json={"model": new_model, "context_length": 16384, "flash_attention": True},
                )
                if load_resp.status_code not in (200, 201):
                    err = load_resp.json().get("error", {})
                    msg = err.get("message", str(load_resp.text)) if isinstance(err, dict) else str(err)
                    raise RuntimeError(msg)
                return load_resp.json()
            return {"status": "already_loaded", "instance_id": new_model}

    async def _ollama_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(f"{self.settings.ollama_base_url}/api/tags")
                resp.raise_for_status()
                return [item["name"] for item in resp.json().get("models", [])]
        except Exception:
            return []

    def _best_available(self, available: list[str], preferred: list[str]) -> str:
        normalized = {m.lower(): m for m in available}
        for target in preferred:
            for lower, original in normalized.items():
                if target.lower() in lower or lower in target.lower():
                    return original
        return available[0] if available else preferred[-1]


def _sanitize_error(msg: str) -> str:
    """Remove API keys and tokens from error messages before showing to the user."""
    import re
    # Strip ?key=... query params (Gemini style)
    msg = re.sub(r"\?key=[^'\s&]+", "?key=***", msg)
    # Strip Bearer tokens
    msg = re.sub(r"Bearer [A-Za-z0-9\-._~+/]+=*", "Bearer ***", msg)
    return msg


def tutor_system_prompt() -> str:
    return (
        "You are an expert Digital SAT tutor. Give concise, step-by-step, beginner-friendly explanations. "
        "Always identify the tested concept, the student's likely misconception, the fastest SAT method, "
        "and a confidence-building next step. Do not invent College Board claims."
    )
