# 🔎 ResearchLens

Paste URLs, get a structured research report where every key point cites the source it came from.

**Live demo:** https://researchlenz.streamlit.app/
*(Free apps sleep after inactivity. If you see a "wake up" button, click it and wait a minute.)*

![ResearchLens screenshot](docs/screenshot.png)

## Problem

Researching a topic means opening many tabs and skimming long pages. ResearchLens does the first pass and shows which source each claim came from, so you can verify it.

## Features

- Fetches and cleans text from one or more URLs; unreachable pages are skipped instead of crashing the run
- Splits long pages into overlapping chunks and summarizes them (map-reduce)
- Produces a structured report: title, summary, key points, open questions, sources
- Every key point carries source citations; sources come from the pages actually fetched, not from the model
- Output is validated with Pydantic; invalid JSON is sent back to the model with the error for automatic retry
- Handles free-tier API limits with request throttling and exponential backoff
- Streamlit UI with Quick and Detailed modes and a Markdown download

## How it works

```
URLs -> fetch and clean -> chunk (~6000 chars, 500 overlap) -> summarize each chunk (map)
     -> combine into a JSON report (reduce) -> validate with Pydantic -> retry on error -> UI
```

Project layout:

```
app.py                Streamlit UI
src/fetcher.py        download a page and keep headings, paragraphs and list items
src/chunker.py        split text into overlapping chunks
src/summarizer.py     map step: summarize each chunk
src/report.py         reduce step: JSON report, validation, retry, Markdown export
src/pipeline.py       connects everything
src/models.py         Pydantic schemas
src/prompts.py        all prompts, versioned (V1, V2, V3)
src/llm.py            API wrapper: throttling, backoff, streaming
tests/                pytest tests for the chunker and models
eval/                 evaluation script and results
failures.md           log of what broke and how I fixed it
```

## Setup

```
git clone https://github.com/fayazahamedofficial/research-assistant.git
cd research-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with a free Gemini API key from aistudio.google.com:

```
GEMINI_API_KEY=your-key-here
```

Run the app:

```
streamlit run app.py
```

Run the tests:

```
python -m pytest -v
```

Run the evaluation (about 50 API calls, takes several minutes on the free tier):

```
python -m eval.run_eval
```

Model names change often. If you get a "model not found" error, set `MODEL=` in `.env` to a current free model.

## Evaluation

I compared three versions of the report prompt on 6 test cases (4 single pages, 2 pairs of pages; all Wikipedia), running each version 3 times per case (18 runs per version). Page summaries were generated once and reused, so every version saw identical input.

| Version | Valid JSON first try | Runs with [n] markers in text | Avg tokens |
|---|---|---|---|
| V1 | 100% (18/18) | 28% (5/18) | 1,376 |
| V2 | 83% (15/18) | 0% | 1,804 |
| V3 | 100% (18/18) | 0% | 1,515 |

All versions completed 100% of runs (failed validation is retried automatically), and no key point lacked a citation or pointed to a non-existent source.

What changed between versions:

- **V1 to V2:** forbade `[n]` markers inside the point text. The leak went from 5 of 18 runs to 0.
- **V2 to V3:** added a rule that `open_questions` must be plain strings. V2 had returned objects on the Black hole topic; V3 had no first-try failures.

**Not measured:** whether each cited source really supports its key point. The automatic checks only confirm that every key point has a citation pointing to a real source, not that the claim is correct.

**Limits of this evaluation:** small sample (6 cases, 18 runs per version), Wikipedia pages only, and reports use only the first 2 chunks of each page. Runs on the same case share the same input, so differences of a few runs may be chance. The live app uses a similar prompt with added length rules that was not evaluated separately.

## What I learned and what failed

Full log in [failures.md](failures.md). Highlights:

- Raw page text was full of menus, infobox labels and footnote markers like `[ 2 ]`. Keeping only headings, paragraphs and list items, then cleaning footnotes with a regex, fixed it.
- Some pages showed garbled characters in titles (wrong encoding guess). Passing raw bytes to BeautifulSoup fixed it.
- The Quick/Detailed selector first changed only the number of chunks read, so both modes looked alike. Length rules now live in the report prompt.
- Prompt V1 sometimes wrote citation markers inside the point text; V2 fixed that.
- V2 sometimes returned `open_questions` as objects instead of strings; the retry loop recovered it and V3 added a format rule.
- Free API tiers limit requests per minute and retire model names, so calls are throttled and retried with backoff, and the model name is configurable.

## Limitations

- Only the first few chunks of each page are summarized (2 in Quick mode, 6 in Detailed), so later sections of long pages can be missing from the report.
- Tested mainly on Wikipedia. Paywalled or JavaScript-heavy sites may fail or return little text.
- Summaries can still contain mistakes; check the cited source.
- Runs on a free API tier with rate limits. The demo limits each session to a few reports and 3 URLs.

## Future work

- Measure citation accuracy (does the cited page support the claim?)
- Web search for topic-only input
- Follow-up chat about a generated report
- PDF upload and saved report history