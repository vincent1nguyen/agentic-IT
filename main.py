import sqlite3
from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, StringConstraints

from knowledge_repository import search_documents

from llm import LLMConfigurationError, LLMProviderError, generate_answer

# Reusable validated string type:
# removes leading/trailing whitespace and requires at least one character.
QuestionText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class QuestionRequest(BaseModel):
    # Field name: question; expected type: QuestionText
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
        context = search_documents(
            request.question, permitted_sensitivities=("public",), service="vpn", limit=3
        )
    except (sqlite3.Error, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge search is temporarily unavailable.",
        ) from exc

    if not context:
        return QuestionResponse(
            answer="I couldn't find supporting information in the VPN documentation. "
            "Please provide more details about your VPN question.",
            sources=[],
        )

    try:
        answer = generate_answer(request.question, context)
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
        sources=[result.source_reference for result in context],
    )
