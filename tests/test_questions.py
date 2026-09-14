from fastapi.testclient import TestClient
import json
import sqlite3
from functools import partial
import pytest

import main
from knowledge_repository import load_seed, search_documents
from llm import LLMConfigurationError, LLMProviderError


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def mock_search(monkeypatch, search_result):
    monkeypatch.setattr(main, "search_documents", lambda *args, **kwargs: [search_result])


def test_question_returns_generated_answer(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "generate_answer",
        lambda question, context: f"Troubleshooting guidance for: {question}",
    )

    response = client.post("/questions", json={"question": "Wi-Fi is unavailable"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Troubleshooting guidance for: Wi-Fi is unavailable",
        "sources": ["fixture://vpn-guide"],
    }


def test_question_rejects_blank_input() -> None:
    response = client.post("/questions", json={"question": "   "})

    assert response.status_code == 422


def test_question_handles_missing_configuration(monkeypatch) -> None:
    def raise_configuration_error(question, context) -> str:
        raise LLMConfigurationError("secret internal configuration detail")

    monkeypatch.setattr(main, "generate_answer", raise_configuration_error)

    response = client.post("/questions", json={"question": "VPN will not connect"})

    assert response.status_code == 503
    assert response.json() == {"detail": "AI response generation is not configured."}


def test_question_handles_provider_failure(monkeypatch) -> None:
    def raise_provider_error(question, context) -> str:
        raise LLMProviderError("raw provider detail")

    monkeypatch.setattr(main, "generate_answer", raise_provider_error)

    response = client.post("/questions", json={"question": "VPN will not connect"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "AI response generation is temporarily unavailable."
    }


@pytest.mark.parametrize("question", ["VPN profile", "astronomy"])
def test_question_retrieves_only_public_vpn_context(
    monkeypatch, tmp_path, document_record, question
):
    seed, database = tmp_path / "seed.json", tmp_path / "knowledge.db"
    seed.write_text(json.dumps({"documents": [
        document_record,
        document_record | {"id": "private", "sensitivity": "restricted",
                           "content": "Secret VPN profile instructions."},
        document_record | {"id": "other-service", "service": "wifi"},
    ]}), encoding="utf-8")
    load_seed(seed, database)
    monkeypatch.setattr(main, "search_documents", partial(search_documents, database_path=database))
    calls = []

    def answer(received_question, context):
        calls.append((received_question, context))
        return "Select the assigned VPN profile. [1]"

    monkeypatch.setattr(main, "generate_answer", answer)
    response = client.post("/questions", json={"question": question})
    assert response.status_code == 200
    if question == "astronomy":
        assert calls == []
        assert response.json()["sources"] == []
        assert "couldn't find supporting information" in response.json()["answer"]
    else:
        assert len(calls) == 1
        assert calls[0][0] == question
        assert [result.id for result in calls[0][1]] == ["vpn-guide"]
        assert calls[0][1][0].excerpt == document_record["content"]
        assert response.json() == {
            "answer": "Select the assigned VPN profile. [1]",
            "sources": ["fixture://vpn-guide"],
        }


@pytest.mark.parametrize("error", [sqlite3.OperationalError("private path"), ValueError("bad record")])
def test_question_handles_search_failure(monkeypatch, error):
    def fail(*args, **kwargs):
        raise error

    def unexpected_model_call(*args):
        pytest.fail("Model must not run when search fails")

    monkeypatch.setattr(main, "search_documents", fail)
    monkeypatch.setattr(main, "generate_answer", unexpected_model_call)
    response = client.post("/questions", json={"question": "VPN"})
    assert response.status_code == 503
    assert response.json() == {"detail": "Knowledge search is temporarily unavailable."}
