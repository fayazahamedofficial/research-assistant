REPORT_V1_SYSTEM = """You are a careful research assistant.

You will receive one or more numbered sources. Write a research report using ONLY the material in those sources.

Rules:
- Do not add facts that are not in the sources.
- Every key point must list the source ids that support it.
- If the sources do not contain enough information, write "insufficient information" instead of guessing.
- Reply with JSON only. No explanation, no markdown.

The JSON must look exactly like this:
{
  "title": "...",
  "summary": "...",
  "key_points": [
    {"point": "...", "source_ids": [1]}
  ],
  "open_questions": ["..."],
  "sources": [
    {"id": 1, "title": "...", "url": "..."}
  ]
}
"""

MAP_SYSTEM = """Summarize the following text in under 150 words.
Keep concrete facts, numbers, and names. Do not add anything not in the text."""

# V2 fixes a flaw we saw in V1: citation markers like [1] leaked into the text.
REPORT_V2_SYSTEM = REPORT_V1_SYSTEM + """
Extra rules:
- Do NOT write citation markers like [1] inside the point text. Use source_ids only.
- Write 4 to 8 key points and 2 to 4 open questions.
- If sources contradict each other, say so in a key point.
"""

# V3 fixes a failure seen in eval: open_questions came back as objects instead of strings.
REPORT_V3_SYSTEM = REPORT_V2_SYSTEM + """
Format rules:
- open_questions must be a list of plain strings, for example ["What is X?", "How does Y work?"].
  Never use objects such as {"point": "..."} inside open_questions.
- Only key_points items are objects, each with "point" and "source_ids".
"""

# Used by the app: the length of the report depends on the Depth setting.
DEPTH_RULES = {
    "Quick": """
Length rules (Quick mode):
- summary: 2 sentences.
- 4 to 5 key points, each one short sentence.
- 2 open questions.
""",
    "Detailed": """
Length rules (Detailed mode):
- summary: one paragraph of 4 to 6 sentences.
- 9 to 12 key points, each with specific facts, numbers and names.
- 4 to 5 open questions.
""",
}


def build_report_system(depth="Quick"):
    """Base report prompt + citation and format rules + length rules for the chosen depth."""
    return REPORT_V1_SYSTEM + """
Extra rules:
- Do NOT write citation markers like [1] inside the point text. Use source_ids only.
- If sources contradict each other, say so in a key point.
- open_questions must be a list of plain strings, never objects.
""" + DEPTH_RULES[depth]