import json
from typing import Any

from django.conf import settings
from openai import OpenAI

from .exceptions import AIServiceError


def analyze_code(prompt: str) -> dict[str, Any]:
    """
    Analyze code with LLM and return parsed JSON.
    """
    if not settings.OPENAI_API_KEY:
        raise AIServiceError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict senior code reviewer. Return only JSON that follows "
                        "the expected response schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
    except Exception as exc:  # noqa: BLE001
        raise AIServiceError(f"OpenAI request failed: {exc}") from exc

    text_output = getattr(response, "output_text", None)
    if not text_output:
        raise AIServiceError("OpenAI response did not include text output.")

    try:
        return json.loads(text_output)
    except json.JSONDecodeError as exc:
        raise AIServiceError("OpenAI response was not valid JSON.") from exc
