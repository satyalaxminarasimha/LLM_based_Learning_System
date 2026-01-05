import httpx

from .config import get_settings

settings = get_settings()


async def ask_ai(message: str, syllabus_context: list[str] | None = None) -> tuple[str, str]:
    """Return AI reply and provider name. Fallback to deterministic stub when no API key."""
    if not settings.openai_api_key:
        context = " | ".join(syllabus_context or [])
        reply = (
            "[AI stub] "
            + (f"Context: {context}. " if context else "")
            + f"Answering briefly: {message[:300]}"
        )
        return reply, "stub"

    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": "You are a concise educational assistant."},
            {"role": "user", "content": message},
        ],
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()
        return reply, "openai"
