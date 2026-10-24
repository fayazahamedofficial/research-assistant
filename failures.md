# Failures log

What broke, why, and how I fixed it.

## Fetching and cleaning
- **Wikipedia text was mostly junk.** Plain `get_text` split sentences at every link and included infobox labels and menu text. Fixed by keeping only headings, paragraphs and list items inside the main content area.
- **Footnote markers like `[ 2 ]` and stray spaces before punctuation** polluted the text. Fixed with a small regex clean-up function.
- **Garbled characters in some page titles** (a dash showed as `â`). `requests` guessed the wrong encoding. Fixed by passing raw bytes to BeautifulSoup.
- **Unreachable URLs** raise a custom `FetchError`. The pipeline skips them and still builds a report from the remaining pages.

## Model output
- **Prompt V1 wrote citation markers like `[1]` inside the point text** in 5 of 18 eval runs. V2 forbids this; 0 leaks in 18 runs.
- **V2 returned `open_questions` as objects (`{"point": ...}`) instead of strings** on the Black hole topic, failing validation on the first try. The retry loop recovered it by sending the Pydantic error back. V3 adds an explicit format rule.
- **Quick and Detailed modes looked the same.** Depth only changed how many chunks were read, while one prompt controlled the report size. Length rules now depend on the selected depth.

## API and environment
- **The model name stopped working** (`404 model no longer available to new users`). Free-tier model names change often, so the model is now configurable through `MODEL` in `.env`.
- **Edits that "did nothing."** Several times Python ran an old version because the file wasn't saved, or the new code went into the wrong file. Lesson: check the unsaved dot on the editor tab, and verify with a search (`Select-String`) before debugging.

## Known limitations (not fixed)
- Only the first few chunks of each page are summarized, so later sections of long pages can be missing from the report.
- Citation correctness (does the cited page support the claim?) was not measured; the eval only checks that citations point to real sources.
- Tested mainly on Wikipedia pages. Paywalled or JavaScript-heavy sites may return little or no text.