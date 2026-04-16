import json
import re
import time
from typing import Any

from django.conf import settings
try:
    from google import genai
except ImportError:  # pragma: no cover - fallback for namespace import edge cases
    import google.genai as genai

from .exceptions import AIServiceError


def _parse_json_output(text_output: str) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Parse model output with a few safe fallbacks for wrapped JSON.
    """
    candidates = [text_output.strip()]

    # Common model behavior: wrap JSON in markdown fences.
    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text_output, flags=re.DOTALL)
    if fenced_match:
        candidates.append(fenced_match.group(1).strip())

    # Recover first JSON array/object if extra prose is present.
    start_positions = [pos for pos in (text_output.find("["), text_output.find("{")) if pos != -1]
    if start_positions:
        start = min(start_positions)
        end_array = text_output.rfind("]")
        end_object = text_output.rfind("}")
        end_candidates = [pos for pos in (end_array, end_object) if pos >= start]
        if end_candidates:
            end = max(end_candidates)
            candidates.append(text_output[start : end + 1].strip())

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    raise AIServiceError("Gemini response was not valid JSON.")


def analyze_code(prompt: str) -> dict[str, Any]:
    """
    Analyze code with LLM and return parsed JSON.
    """
    if not settings.GEMINI_API_KEY:
        raise AIServiceError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    full_prompt = (
        "You are a strict senior code reviewer. Return only JSON that follows "
        "the expected response schema.\n\n"
        f"{prompt}"
    )
    retryable_statuses = {429, 500, 502, 503, 504}
    max_retries = max(settings.GEMINI_MAX_RETRIES, 0)
    text_output: str | None = None

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=full_prompt,
            )
            text_output = response.text
            if text_output:
                break
            raise AIServiceError("Gemini response did not include text output.")
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            status_code = None
            for code in retryable_statuses:
                if f"{code}" in message:
                    status_code = code
                    break

            is_retryable = status_code in retryable_statuses
            if attempt == max_retries:
                raise AIServiceError(f"Gemini request failed: {exc}") from exc
            if not is_retryable:
                raise AIServiceError(f"Gemini request failed: {exc}") from exc
            time.sleep(settings.GEMINI_RETRY_BACKOFF_SECONDS * (2**attempt))
            continue
    if not text_output:
        raise AIServiceError("Gemini response did not include text output.")

    return _parse_json_output(text_output)
