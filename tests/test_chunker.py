from src.chunker import chunk_text


def make_text(n=10):
    return "\n".join(f"P{i:02d}" + "x" * 27 for i in range(n))  # 10 paragraphs of 30 chars


def test_empty_text():
    assert chunk_text("") == []


def test_short_text_is_one_chunk():
    assert len(chunk_text("hello world")) == 1


def test_chunks_are_not_too_big():
    for c in chunk_text(make_text(), max_chars=100, overlap=40):
        assert len(c) <= 100 + 40 + 2


def test_no_text_is_lost():
    joined = "\n".join(chunk_text(make_text(), max_chars=100, overlap=40))
    for i in range(10):
        assert f"P{i:02d}" in joined


def test_chunks_overlap():
    chunks = chunk_text(make_text(), max_chars=100, overlap=40)
    assert len(chunks) > 1
    assert chunks[0].split("\n")[-1] in chunks[1]


def test_giant_paragraph_is_split():
    assert len(chunk_text("a" * 250, max_chars=100, overlap=20)) >= 3