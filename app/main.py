from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app import ai, extractor
from app.chunking import chunk_paragraphs
from app.schemas import (
    URLRequest,
    SummarizeRequest,
    ReadingModeRequest,
    ExplainRequest,
    QuizRequest,
    TextRequest,
)

app = FastAPI(title="AI Reading Comfort Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------- Feature 1: URL Reader / Focus Mode / Smart Chunking ----------------

@app.post("/api/extract")
def extract(req: URLRequest):
    """
    Fetches a URL, strips ads/sidebars/popups (Focus Mode), and returns clean
    article content already split into logical reading sections (Smart Chunking).
    """
    try:
        article = extractor.extract_article(req.url)
    except extractor.ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    chunks = chunk_paragraphs(article["paragraphs"])

    return {
        "title": article["title"],
        "text": article["text"],
        "images": article["images"],
        "word_count": article["word_count"],
        "chunks": chunks,
    }


# ---------------- Feature 2: Summarize ----------------

@app.post("/api/summarize")
def summarize(req: SummarizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        summary = ai.summarize(req.text, req.length)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"summary": summary, "length": req.length}


# ---------------- Feature 3: Reading Modes ----------------

@app.post("/api/reading-mode")
def reading_mode(req: ReadingModeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        rewritten = ai.apply_reading_mode(req.text, req.mode)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"text": rewritten, "mode": req.mode}


# ---------------- Feature 4: Difficulty Analyzer ----------------

@app.post("/api/analyze")
def analyze(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    word_count = len(req.text.split())
    try:
        result = ai.analyze_difficulty(req.text, word_count)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ---------------- Feature 5: AI Highlighting ----------------

@app.post("/api/highlights")
def highlights(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        result = ai.extract_highlights(req.text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ---------------- Extra: AI Tutor (explain a selected passage) ----------------

@app.post("/api/explain")
def explain(req: ExplainRequest):
    if not req.passage.strip():
        raise HTTPException(status_code=400, detail="passage is required")
    try:
        explanation = ai.explain_passage(req.passage, req.context)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"explanation": explanation}


# ---------------- Extra: Quiz / Flashcards ----------------

@app.post("/api/quiz")
def quiz(req: QuizRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        result = ai.generate_quiz(req.text, req.kind, req.count)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ---------------- Extra: Knowledge Graph ----------------

@app.post("/api/knowledge-graph")
def knowledge_graph(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        result = ai.knowledge_graph(req.text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ---------------- Serve frontend ----------------
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def index():
    return FileResponse("frontend/index.html")
