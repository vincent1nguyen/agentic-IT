from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, StringConstraints

from llm import LLMConfigurationError, LLMProviderError, generate_answer


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
    try:
        answer = generate_answer(request.question)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI response generation is not configured.",
        ) from exc
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI response generation is temporarily unavailable.",
        ) from exc

    return QuestionResponse(
        answer=answer,
        sources=[],
    )
