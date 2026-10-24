import json
from pydantic import ValidationError
from src.llm import call
from src.models import Report
from src.prompts import build_report_system

MAX_ATTEMPTS = 3


def strip_fences(text):
    """Models often wrap JSON in ```json ... ```. Remove that wrapper."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return text.strip()


def generate_report(sources_text, system=None, max_attempts=MAX_ATTEMPTS, stats=None):
    """REDUCE step: turn summaries into a validated Report, retrying on bad JSON.
    If a dict is passed as `stats`, it is filled with attempts and token counts."""
    system = system or build_report_system("Quick")
    stats = stats if stats is not None else {}
    stats.update(attempts=0, input_tokens=0, output_tokens=0)
    messages = [{"role": "user", "content": sources_text}]

    for attempt in range(1, max_attempts + 1):
        raw, usage = call(messages, system=system)
        stats["attempts"] = attempt
        stats["input_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
        stats["output_tokens"] += getattr(usage, "completion_tokens", 0) or 0
        try:
            return Report.model_validate(json.loads(strip_fences(raw)))
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"[attempt {attempt}] failed: {type(e).__name__}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"Your last output failed validation with this error: {e}\n"
                           "Return corrected JSON only.",
            })

    raise RuntimeError(f"Could not get valid JSON after {max_attempts} attempts")


def to_markdown(report):
    lines = [f"# {report.title}", "", "## Summary", report.summary, "", "## Key points"]
    for kp in report.key_points:
        refs = " ".join(f"[{i}]" for i in kp.source_ids)
        lines.append(f"- {kp.point} {refs}")
    lines += ["", "## Open questions"] + [f"- {q}" for q in report.open_questions]
    lines += ["", "## Sources"] + [f"{s.id}. [{s.title}]({s.url})" for s in report.sources]
    return "\n".join(lines)