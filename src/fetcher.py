import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (ResearchLens learning project)"}
MIN_CHARS = 200


class FetchError(Exception):
    """Raised when a page can't be fetched or has no usable text."""


def clean(piece):
    """Tidy one piece of text."""
    piece = re.sub(r"\[\s*\d+\s*\]", "", piece)       # remove footnote markers like [ 2 ]
    piece = re.sub(r"\s+([,.;:!?)])", r"\1", piece)   # "bee ." -> "bee."
    piece = re.sub(r"\(\s+", "(", piece)              # "( i.e." -> "(i.e."
    return piece.strip()


def fetch_url(url, timeout=15):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise FetchError(f"Could not fetch {url}: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove parts that are never the article itself
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url

    # Look inside the main content area, falling back to the whole page
    main = soup.find("main") or soup.find("article") or soup.body or soup

    # Keep only headings, paragraphs and list items
    parts = []
    for el in main.find_all(["h1", "h2", "h3", "p", "li"]):
        piece = clean(el.get_text(" ", strip=True))
        if el.name.startswith("h") or len(piece) > 40:
            parts.append(piece)
    text = "\n".join(parts)

    if len(text) < MIN_CHARS:
        raise FetchError(f"Page has too little text ({len(text)} chars): {url}")

    return {"title": title, "url": url, "text": text}