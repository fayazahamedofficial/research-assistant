import json
from pathlib import Path
from pydantic import ValidationError
from src.llm import call
from src.models import Report
from src.prompts import REPORT_V2_SYSTEM
from src.report import strip_fences

digest = (Path(__file__).parent / "cache" / "topic_4.txt").read_text(encoding="utf-8")

for run in range(1, 4):
    raw, _ = call([{"role": "user", "content": digest}], system=REPORT_V2_SYSTEM)
    try:
        Report.model_validate(json.loads(strip_fences(raw)))
        print(f"run {run}: OK")
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"run {run}: FAILED\n{e}\n")
        print("RAW (first 600 chars):", raw[:600], "\n")