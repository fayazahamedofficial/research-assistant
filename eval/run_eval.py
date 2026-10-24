import csv
import json
import random
import re
import time
from pathlib import Path

from src.fetcher import fetch_url, FetchError
from src.prompts import REPORT_V1_SYSTEM, REPORT_V2_SYSTEM
from src.report import generate_report
from src.summarizer import build_digest

VERSIONS = {"V1": REPORT_V1_SYSTEM, "V2": REPORT_V2_SYSTEM}
REPEATS = 2        # run each version this many times per topic (the AI varies)
MAX_CHUNKS = 2     # chunks per page, keeps API usage low

HERE = Path(__file__).parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)


def get_digest(i, urls):
    """Summarize the pages once and save the result, so reruns are cheap."""
    path = CACHE / f"topic_{i}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    pages = [fetch_url(u) for u in urls]
    digest = build_digest(pages, max_chunks=MAX_CHUNKS)
    path.write_text(digest, encoding="utf-8")
    return digest


def check(report, n_sources):
    """Automatic checks on one report."""
    points = report.key_points
    return {
        "n_key_points": len(points),
        "uncited": sum(1 for kp in points if not kp.source_ids),
        "bad_citation_ids": sum(
            1 for kp in points for i in kp.source_ids if i < 1 or i > n_sources
        ),
        "marker_leaks": sum(1 for kp in points if re.search(r"\[\d+\]", kp.point)),
    }


def avg(rows, key):
    return sum(r[key] for r in rows) / len(rows) if rows else 0


def main():
    random.seed(1)
    topics = json.loads((HERE / "topics.json").read_text(encoding="utf-8"))
    rows, samples = [], []

    for i, urls in enumerate(topics, start=1):
        print(f"\n=== Topic {i}/{len(topics)}: {urls}")
        try:
            digest = get_digest(i, urls)
        except FetchError as e:
            print("  SKIPPED:", e)
            continue

        for version, system in VERSIONS.items():
            for rep in range(1, REPEATS + 1):
                print(f"  {version} run {rep}...")
                stats = {}
                start = time.time()
                row = {"topic": i, "version": version, "repeat": rep}
                try:
                    report = generate_report(digest, system=system, stats=stats)
                    row.update(ok=1, **check(report, len(urls)))
                    if rep == 1:
                        samples.append((i, version, urls, report))
                except Exception as e:
                    print("  FAILED:", e)
                    row.update(ok=0, n_key_points=0, uncited=0,
                               bad_citation_ids=0, marker_leaks=0)
                row["first_try"] = int(row["ok"] == 1 and stats.get("attempts") == 1)
                row["tokens"] = stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
                row["seconds"] = round(time.time() - start, 1)
                rows.append(row)

    if not rows:
        print("No results.")
        return

    # Save every run
    fields = ["topic", "version", "repeat", "ok", "first_try", "n_key_points",
              "uncited", "bad_citation_ids", "marker_leaks", "tokens", "seconds"]
    with open(HERE / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    # Summary table per version
    lines = [
        "| Version | Runs | Valid JSON first try | Completed | Avg key points | "
        "Uncited points | Bad citation ids | Runs with [n] in text | Avg tokens |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for version in VERSIONS:
        r = [x for x in rows if x["version"] == version]
        if not r:
            continue
        lines.append(
            f"| {version} | {len(r)} | {100 * avg(r, 'first_try'):.0f}% | "
            f"{100 * avg(r, 'ok'):.0f}% | {avg(r, 'n_key_points'):.1f} | "
            f"{sum(x['uncited'] for x in r)} | {sum(x['bad_citation_ids'] for x in r)} | "
            f"{100 * sum(1 for x in r if x['marker_leaks'] > 0) / len(r):.0f}% | "
            f"{avg(r, 'tokens'):,.0f} |"
        )
    summary = "\n".join(lines)
    (HERE / "summary.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)

    # Sample key points for YOU to check by hand
    out = ["# Manual citation check",
           "For each point: open the cited source, search for the fact, write yes or no.\n"]
    for i, version, urls, report in samples:
        out.append(f"## Topic {i} - {version}")
        out.append("Sources: " + " | ".join(f"{n}={u}" for n, u in enumerate(urls, 1)))
        for kp in random.sample(report.key_points, min(2, len(report.key_points))):
            out.append(f"- {kp.point}  -> cites {kp.source_ids}  | correct? ")
        out.append("")
    (HERE / "manual_check.md").write_text("\n".join(out), encoding="utf-8")
    print("\nSaved: eval/results.csv, eval/summary.md, eval/manual_check.md")


if __name__ == "__main__":
    main()