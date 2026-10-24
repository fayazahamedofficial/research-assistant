from src.fetcher import fetch_url
from src.summarizer import summarize_chunks

page = fetch_url("https://en.wikipedia.org/wiki/Honey_bee")
summaries = summarize_chunks(page["text"], max_chunks=3)

for i, s in enumerate(summaries, start=1):
    print(f"\n--- Summary {i} ({len(s.split())} words) ---")
    print(s)