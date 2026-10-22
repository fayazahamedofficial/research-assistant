from src.chunker import chunk_text
from src.llm import call
from src.prompts import MAP_SYSTEM


def summarize_chunks(text, max_chunks=None):
    """MAP step: split text into chunks, summarize each one."""
    chunks = chunk_text(text)
    if max_chunks:
        chunks = chunks[:max_chunks]

    summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"  chunk {i}/{len(chunks)}...")
        summary, _ = call([{"role": "user", "content": chunk}], system=MAP_SYSTEM)
        summaries.append(summary.strip())
    return summaries


def build_digest(pages, max_chunks=None):
    """Summarize every page and label each one [Source 1], [Source 2], ..."""
    blocks = []
    for i, page in enumerate(pages, start=1):
        print(f"Summarizing source {i}: {page['title']}")
        summaries = summarize_chunks(page["text"], max_chunks=max_chunks)
        bullets = "\n".join(f"- {s}" for s in summaries)
        blocks.append(
            f"[Source {i}]\nTitle: {page['title']}\nURL: {page['url']}\nSummaries:\n{bullets}"
        )
    return "\n\n".join(blocks)