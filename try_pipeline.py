from src.pipeline import research_from_urls

urls = [
    "https://en.wikipedia.org/wiki/Honey_bee",
    "https://en.wikipedia.org/wiki/Beekeeping",
    "https://thisdoesnotexist12345.com",   # on purpose: should be skipped
]

report, errors = research_from_urls(urls, max_chunks=3)

print("\nSKIPPED:", errors)
print("\nTITLE:", report.title)
print("SUMMARY:", report.summary)
print("\nKEY POINTS:")
for kp in report.key_points:
    print(f"- {kp.point}  (sources: {kp.source_ids})")
print("\nOPEN QUESTIONS:")
for q in report.open_questions:
    print("-", q)
print("\nSOURCES:")
for s in report.sources:
    print(f"{s.id}. {s.title} - {s.url}")