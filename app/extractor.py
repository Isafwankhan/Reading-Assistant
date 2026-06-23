"""
Extracts the main article content from a URL, stripping ads, navs,
sidebars, and other clutter (Focus Mode). Returns clean title + text + images.
"""
import re
import requests
from bs4 import BeautifulSoup
from readability import Document

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

NOISE_TAGS = ["script", "style", "noscript", "iframe", "form", "button", "aside"]


class ExtractionError(Exception):
    pass


def fetch_html(url: str, timeout: int = 12) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ExtractionError(f"Could not fetch URL: {e}")
    return resp.text


def extract_article(url: str) -> dict:
    """
    Returns: {title, html, text, images, word_count}
    """
    html = fetch_html(url)

    doc = Document(html)
    title = (doc.short_title() or "Untitled Article").strip()
    article_html = doc.summary(html_partial=True)

    soup = BeautifulSoup(article_html, "lxml")

    # Focus Mode: strip remaining noise elements
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Collect images before stripping attrs (limit to avoid junk/ad images)
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and src.startswith("http"):
            images.append(src)
    images = images[:8]

    # Build clean text (paragraph-aware, for chunking later)
    paragraphs = []
    for el in soup.find_all(["p", "h1", "h2", "h3", "li", "blockquote"]):
        text = el.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if text and len(text) > 1:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)

    if len(full_text.split()) < 40:
        raise ExtractionError(
            "Could not find enough readable article content at this URL "
            "(page may be paywalled, JS-rendered, or not an article)."
        )

    word_count = len(full_text.split())

    return {
        "title": title,
        "text": full_text,
        "paragraphs": paragraphs,
        "images": images,
        "word_count": word_count,
    }
