import json
from pydantic import ValidationError
from src.llm import call
from src.models import Report
from src.prompts import REPORT_V1_SYSTEM

MAX_ATTEMPTS = 3


def strip_fences(text):
    """Models often wrap JSON in ```json ... ```. Remove that wrapper."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return text.strip()


def generate_report(sources_text, max_attempts=MAX_ATTEMPTS):
    messages = [{"role": "user", "content": sources_text}]

    for attempt in range(1, max_attempts + 1):
        raw, usage = call(messages, system=REPORT_V1_SYSTEM)
        try:
            data = json.loads(strip_fences(raw))
            return Report.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"[attempt {attempt}] failed: {type(e).__name__}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"Your last output failed validation with this error: {e}\n"
                           "Return corrected JSON only.",
            })

    raise RuntimeError(f"Could not get valid JSON after {max_attempts} attempts")