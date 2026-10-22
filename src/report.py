import json
from src.llm import call
from src.models import Report
from src.prompts import REPORT_V1_SYSTEM


def strip_fences(text):
    """Models often wrap JSON in ```json ... ```. Remove that wrapper."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return text.strip()


def generate_report(sources_text):
    raw, usage = call(
        [{"role": "user", "content": sources_text}],
        system=REPORT_V1_SYSTEM,
    )
    print("----- RAW AI OUTPUT -----")
    print(raw)
    print("-------------------------")

    data = json.loads(strip_fences(raw))
    return Report.model_validate(data)