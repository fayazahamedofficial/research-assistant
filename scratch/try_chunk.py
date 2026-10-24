from src.fetcher import fetch_url
from src.chunker import chunk_text

page = fetch_url("https://en.wikipedia.org/wiki/Honey_bee")
chunks = chunk_text(page["text"])

print("Total text:", len(page["text"]), "characters")
print("Number of chunks:", len(chunks))
print("Chunk sizes:", [len(c) for c in chunks])

print("\n----- END of chunk 1 -----")
print(chunks[0][-300:])
print("\n----- START of chunk 2 -----")
print(chunks[1][:300])