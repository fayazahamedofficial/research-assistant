from src.fetcher import fetch_url, FetchError

page = fetch_url("https://en.wikipedia.org/wiki/Honey_bee")
print("TITLE:", page["title"])
print("LENGTH:", len(page["text"]), "characters")
print("\nFIRST 500 CHARACTERS:\n")
print(page["text"][:500])

print("\n----- Now a broken URL -----")
try:
    fetch_url("https://thisdoesnotexist12345.com")
except FetchError as e:
    print("Caught error:", e)