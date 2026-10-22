from pydantic import BaseModel


class Source(BaseModel):
    id: int
    title: str
    url: str


class KeyPoint(BaseModel):
    point: str
    source_ids: list[int]  # which sources support this point


class Report(BaseModel):
    title: str
    summary: str
    key_points: list[KeyPoint]
    open_questions: list[str]
    sources: list[Source]