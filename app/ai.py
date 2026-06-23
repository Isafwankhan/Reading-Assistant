"""
All GenAI calls live here, using Groq's OpenAI-compatible chat completion API.
Model: llama-3.3-70b-versatile (fast + good quality, free tier friendly).
"""
import json
import os
from functools import lru_cache

from groq import Groq

MODEL = "llama-3.3-70b-versatile"


@lru_cache(maxsize=1)
def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Get a free key at https://console.groq.com and export it."
        )
    return Groq(api_key=api_key)


def _chat(system: str, user: str, max_tokens: int = 1024, json_mode: bool = False) -> str:
    client = get_client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return resp.choices[0].message.content.strip()


# ---------- Feature: Summarize ----------

SUMMARY_LENGTHS = {
    "short": "2-3 sentences, the absolute core takeaway only",
    "medium": "a tight 1-2 paragraph summary covering the main points",
    "detailed": "a thorough multi-paragraph summary covering all key arguments, evidence, and conclusions",
}


def summarize(text: str, length: str = "medium") -> str:
    length = length if length in SUMMARY_LENGTHS else "medium"
    system = (
        "You are an expert reading assistant. Summarize articles clearly and "
        "accurately, in plain prose, with no preamble like 'Here is a summary'."
    )
    user = f"Summarize the following article in {SUMMARY_LENGTHS[length]}.\n\nARTICLE:\n{text[:12000]}"
    return _chat(system, user, max_tokens=900)


# ---------- Feature: Reading Modes (simplify / rewrite) ----------

READING_MODES = {
    "student": (
        "Rewrite this for a student studying the topic: clear, well-structured, "
        "keep key terminology but briefly define jargon, use short paragraphs."
    ),
    "professional": (
        "Rewrite this in a concise, professional tone suited for a busy executive: "
        "lead with the bottom line, keep it efficient, no fluff."
    ),
    "child": (
        "Rewrite this so a curious 10-year-old can understand it: simple words, "
        "short sentences, friendly tone, use a relatable analogy if helpful."
    ),
    "quickscan": (
        "Condense this into a fast-scan format: a one-line gist, then 5-8 short "
        "bullet points capturing only the most important facts."
    ),
}


def apply_reading_mode(text: str, mode: str) -> str:
    mode = mode if mode in READING_MODES else "student"
    system = "You are a reading-comfort assistant that rewrites text for clarity and accessibility."
    user = f"{READING_MODES[mode]}\n\nTEXT:\n{text[:12000]}"
    return _chat(system, user, max_tokens=1200)


# ---------- Feature: Difficulty Analyzer ----------

def analyze_difficulty(text: str, word_count: int) -> dict:
    reading_time_min = max(1, round(word_count / 200))
    system = (
        "You analyze text reading difficulty. Respond ONLY with a JSON object, "
        "no other text, matching exactly this shape: "
        '{"level": "Beginner|Intermediate|Advanced", "complexity_score": <int 1-10>, '
        '"reasoning": "<one short sentence>"}'
    )
    user = f"Analyze the reading difficulty of this article:\n\n{text[:8000]}"
    raw = _chat(system, user, max_tokens=200, json_mode=True)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"level": "Intermediate", "complexity_score": 5, "reasoning": "Default estimate."}
    data["reading_time_minutes"] = reading_time_min
    data["word_count"] = word_count
    return data


# ---------- Feature: AI Highlighting / Key Facts ----------

def extract_highlights(text: str) -> dict:
    system = (
        "You extract the most important points from an article. Respond ONLY "
        'with JSON: {"key_points": ["...", "..."], "key_facts": ["...", "..."]}. '
        "5-8 items max per list, each a single concise sentence."
    )
    user = f"Extract key points and key facts from:\n\n{text[:10000]}"
    raw = _chat(system, user, max_tokens=600, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"key_points": [], "key_facts": []}


# ---------- Feature: AI Tutor - explain a paragraph ----------

def explain_passage(passage: str, context: str = "") -> str:
    system = (
        "You are a patient tutor. Explain the given passage in simple, plain "
        "language, as if to someone unfamiliar with the topic. Be concise (3-6 sentences)."
    )
    user = f"Article context (for reference only):\n{context[:3000]}\n\nExplain this passage:\n{passage}"
    return _chat(system, user, max_tokens=350)


# ---------- Extra: Quiz / Flashcards ----------

def generate_quiz(text: str, kind: str = "mcq", count: int = 5) -> dict:
    kind_instructions = {
        "mcq": '{"questions": [{"question": "...", "options": ["A","B","C","D"], "answer": "A"}]}',
        "flashcard": '{"cards": [{"front": "...", "back": "..."}]}',
        "quiz": '{"questions": [{"question": "...", "answer": "..."}]}',
    }
    shape = kind_instructions.get(kind, kind_instructions["mcq"])
    system = (
        f"You generate study materials from articles. Respond ONLY with JSON matching: {shape}. "
        f"Generate exactly {count} items, based only on the article content."
    )
    user = f"Article:\n{text[:9000]}"
    raw = _chat(system, user, max_tokens=1200, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


# ---------- Extra: Knowledge Graph ----------

def knowledge_graph(text: str) -> dict:
    system = (
        "Extract a simple knowledge graph from the article. Respond ONLY with JSON: "
        '{"topic": "...", "concepts": [{"name": "...", "description": "...", '
        '"related_to": ["<other concept name>", ...]}]}. Limit to 5-8 concepts.'
    )
    user = f"Article:\n{text[:9000]}"
    raw = _chat(system, user, max_tokens=900, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"topic": "Unknown", "concepts": []}
