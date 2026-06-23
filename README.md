# AI Reading Comfort Assistant

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-000?logo=vercel)](https://reading-assistant-six.vercel.app)

**🌐 Live deployment:** [https://reading-assistant-six.vercel.app](https://reading-assistant-six.vercel.app)

A FastAPI backend + single-page frontend that turns any article URL into a
comfortable, AI-enhanced reading experience: clean Focus Mode extraction,
smart chunking, multi-length summaries, reading-mode rewrites, difficulty
analysis, AI highlighting, an AI tutor for explaining passages, quiz
generation, and a knowledge graph extractor — plus dark/sepia/high-contrast/
dyslexia-friendly themes and built-in text-to-speech.

## Stack
- **Backend:** FastAPI
- **GenAI:** Groq (`llama-3.3-70b-versatile`) — fast + free-tier friendly
- **Scraping:** `readability-lxml` + BeautifulSoup (Focus Mode extraction)
- **Frontend:** Single-file HTML/CSS/JS (no build step), browser `SpeechSynthesis` for TTS
- **DB:** none in this MVP (stateless) — see "Next steps" to add Postgres for history/saved articles

## Setup

```bash
cd reading-assistant
pip install -r requirements.txt

# Get a free key at https://console.groq.com
export GROQ_API_KEY="your-key-here"

uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — paste any article URL and click "Read".

## What's implemented (MVP scope)

| Feature | Endpoint | Notes |
|---|---|---|
| URL Reader / Focus Mode | `POST /api/extract` | Strips ads/nav/sidebars, returns clean text + images |
| Smart Chunking | (part of `/api/extract`) | Heuristic paragraph grouping into logical sections, ~180 words/section |
| Summarize (short/medium/detailed) | `POST /api/summarize` | |
| Reading Modes (student/professional/child/quick-scan) | `POST /api/reading-mode` | |
| Difficulty Analyzer | `POST /api/analyze` | Level, complexity score, reading time |
| AI Highlighting | `POST /api/highlights` | Key points + key facts |
| AI Tutor (explain selection) | `POST /api/explain` | Select text in the article, click "Explain selected text" |
| Quiz Generator | `POST /api/quiz` | MCQ by default; `kind` also supports `flashcard`/`quiz` |
| Knowledge Graph | `POST /api/knowledge-graph` | Returns topic + concepts + relations as JSON (not yet wired into the frontend UI) |
| Theme Generator (dark/sepia/high-contrast/dyslexia) | frontend-only | CSS variable swap, instant |
| Text-to-Speech | frontend-only | Browser `SpeechSynthesis` API — zero backend cost/latency |

## Deliberately deferred (not in MVP)
- **Postgres** persistence (saved articles, reading history, user accounts) — stateless for now, easy to bolt on later with a `articles` + `summaries` table.
- **Next.js/Tailwind/Shadcn frontend** — shipped a single-file HTML app instead to keep this runnable in one pass; the API is fully decoupled so a Next.js frontend can swap in without backend changes.
- **Knowledge graph visualization** — endpoint exists and returns structured JSON; rendering it as an actual graph (e.g. with D3 or a tree diagram) is a nice follow-up for portfolio polish.
- **AI-driven theme/color analysis of the *original* page** — the four reading themes are pre-built (not AI-generated per-page); could extend `analyze_difficulty`-style call to inspect page contrast and recommend a theme.

## Project structure
```
reading-assistant/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── extractor.py      # URL fetch + Focus Mode extraction
│   ├── chunking.py       # Smart Chunking heuristic
│   ├── ai.py              # All Groq LLM calls
│   └── schemas.py        # Pydantic request models
├── frontend/
│   └── index.html        # Single-file UI (themes + TTS + all features)
├── requirements.txt
└── README.md
```

## Known limitations
- Sites that render content via JS (heavy SPA news sites) won't extract well with `readability-lxml` alone — a future upgrade could add a headless-browser fallback (Playwright) for those.
- No auth/rate-limiting — fine for a portfolio demo, add before any public deployment.
