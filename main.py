from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, StringConstraints


QuestionText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class QuestionRequest(BaseModel):
    question: QuestionText

class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]

app = FastAPI(title="AI IT Knowledge Assistant API")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/questions", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(
        answer="Your question was received. AI response generation is not connected yet.",
        sources=[],
    )
