from pydantic import ValidationError
from src.models import Report

good = {
    "title": "How Bees Make Honey",
    "summary": "Bees turn nectar into honey by evaporation and enzymes.",
    "key_points": [
        {"point": "Bees collect nectar from flowers.", "source_ids": [1]},
        {"point": "Enzymes break nectar down into simple sugars.", "source_ids": [1, 2]},
    ],
    "open_questions": ["How does weather affect honey quality?"],
    "sources": [
        {"id": 1, "title": "Bee Guide", "url": "https://example.com/bees"},
        {"id": 2, "title": "Honey Science", "url": "https://example.com/honey"},
    ],
}

report = Report.model_validate(good)
print("VALID!")
print(report.title)
print(report.key_points[1].source_ids)

# Now break it on purpose
bad = dict(good)
bad["key_points"] = [{"point": "Bees are cool", "source_ids": "one"}]
del bad["summary"]

try:
    Report.model_validate(bad)
except ValidationError as e:
    print("\nINVALID! Pydantic says:\n")
    print(e)