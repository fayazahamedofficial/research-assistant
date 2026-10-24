from src.fetcher import fetch_url, FetchError
from src.models import Source
from src.prompts import build_report_system
from src.report import generate_report
from src.summarizer import build_digest


def research_from_urls(urls, max_chunks=None, depth="Quick"):
    pages, errors = [], []
    for url in urls:
        try:
            pages.append(fetch_url(url))
        except FetchError as e:
            errors.append(str(e))  # one bad URL must not kill the whole report

    if not pages:
        raise ValueError("None of the URLs could be fetched:\n" + "\n".join(errors))

    digest = build_digest(pages, max_chunks=max_chunks)
    print("Writing the final report...")
    report = generate_report(digest, system=build_report_system(depth))

    # Don't trust the AI for sources: use the real ones we fetched
    report.sources = [Source(id=i, title=p["title"], url=p["url"])
                      for i, p in enumerate(pages, start=1)]

    # Drop any citation pointing to a source that doesn't exist
    valid_ids = {s.id for s in report.sources}
    for kp in report.key_points:
        kp.source_ids = [i for i in kp.source_ids if i in valid_ids]

    return report, errors