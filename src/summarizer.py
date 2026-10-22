from src.chunker import chunk_text
from src.llm import call
from src.prompts import MAP_SYSTEM


def summarize_chunks(text, max_chunks=None):
    """MAP step: split text into chunks, summarize each one.
    Returns a list of short summaries."""
    chunks = chunk_text(text)
    if max_chunks:
        chunks = chunks[:max_chunks]

    summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {i}/{len(chunks)}...")
        summary, _ = call([{"role": "user", "content": chunk}], system=MAP_SYSTEM)
        summaries.append(summary.strip())
    return summaries