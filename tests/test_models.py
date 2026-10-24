import pytest
from pydantic import ValidationError
from src.models import Report

GOOD = {
    "title": "T",
    "summary": "S",
    "key_points": [{"point": "P", "source_ids": [1]}],
    "open_questions": ["Q?"],
    "sources": [{"id": 1, "title": "A", "url": "https://example.com"}],
}


def test_valid_report():
    assert Report.model_validate(GOOD).title == "T"


def test_missing_summary_fails():
    bad = dict(GOOD)
    del bad["summary"]
    with pytest.raises(ValidationError):
        Report.model_validate(bad)


def test_source_ids_must_be_a_list():
    bad = dict(GOOD, key_points=[{"point": "P", "source_ids": "one"}])
    with pytest.raises(ValidationError):
        Report.model_validate(bad)