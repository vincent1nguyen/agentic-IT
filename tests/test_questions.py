from fastapi.testclient import TestClient

import main
from llm import LLMConfigurationError, LLMProviderError


client = TestClient(main.app)


def test_question_returns_generated_answer(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "generate_answer",
        lambda question: f"Troubleshooting guidance for: {question}",
    )

    response = client.post("/questions", json={"question": "Wi-Fi is unavailable"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Troubleshooting guidance for: Wi-Fi is unavailable",
        "sources": [],
    }


def test_question_rejects_blank_input() -> None:
    response = client.post("/questions", json={"question": "   "})

    assert response.status_code == 422


def test_question_handles_missing_configuration(monkeypatch) -> None:
    def raise_configuration_error(question: str) -> str:
        raise LLMConfigurationError("secret internal configuration detail")

    monkeypatch.setattr(main, "generate_answer", raise_configuration_error)

    response = client.post("/questions", json={"question": "VPN will not connect"})

    assert response.status_code == 503
    assert response.json() == {"detail": "AI response generation is not configured."}


def test_question_handles_provider_failure(monkeypatch) -> None:
    def raise_provider_error(question: str) -> str:
        raise LLMProviderError("raw provider detail")

    monkeypatch.setattr(main, "generate_answer", raise_provider_error)

    response = client.post("/questions", json={"question": "VPN will not connect"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "AI response generation is temporarily unavailable."
    }
