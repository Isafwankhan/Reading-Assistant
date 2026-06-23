from pydantic import BaseModel


class URLRequest(BaseModel):
    url: str


class SummarizeRequest(BaseModel):
    text: str
    length: str = "medium"  # short | medium | detailed


class ReadingModeRequest(BaseModel):
    text: str
    mode: str = "student"  # student | professional | child | quickscan


class ExplainRequest(BaseModel):
    passage: str
    context: str = ""


class QuizRequest(BaseModel):
    text: str
    kind: str = "mcq"  # mcq | flashcard | quiz
    count: int = 5


class TextRequest(BaseModel):
    text: str
