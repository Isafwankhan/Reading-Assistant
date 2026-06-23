"""
Smart Chunking: splits a long article's paragraphs into logical, readable
sections (instead of one huge wall of text). Heuristic-based (fast, free,
no LLM call) - groups paragraphs until a target word budget per chunk,
preferring to break right before a heading-like short paragraph.
"""

TARGET_WORDS_PER_CHUNK = 180


def chunk_paragraphs(paragraphs: list[str], target_words: int = TARGET_WORDS_PER_CHUNK) -> list[dict]:
    chunks = []
    current: list[str] = []
    current_words = 0

    def looks_like_heading(p: str) -> bool:
        return len(p.split()) <= 8 and not p.endswith((".", "?", "!"))

    for para in paragraphs:
        words = len(para.split())

        if current and looks_like_heading(para) and current_words >= target_words * 0.5:
            chunks.append(current)
            current, current_words = [], 0

        current.append(para)
        current_words += words

        if current_words >= target_words:
            chunks.append(current)
            current, current_words = [], 0

    if current:
        chunks.append(current)

    return [
        {
            "index": i + 1,
            "text": "\n\n".join(c),
            "word_count": sum(len(p.split()) for p in c),
        }
        for i, c in enumerate(chunks)
    ]
