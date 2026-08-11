from types import SimpleNamespace

import pytest

import llm


def test_generate_answer_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(llm.LLMConfigurationError):
        llm.generate_answer("How should I diagnose a VPN failure?")


def test_generate_answer_uses_configured_model(monkeypatch) -> None:
    captured_request: dict[str, str] = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured_request.update(kwargs)
            return SimpleNamespace(output_text="  Check the VPN configuration.  ")

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm, "OpenAI", lambda api_key: FakeClient())

    answer = llm.generate_answer("How should I diagnose a VPN failure?")

    assert answer == "Check the VPN configuration."
    assert captured_request == {
        "model": "test-model",
        "instructions": llm.SYSTEM_INSTRUCTIONS,
        "input": "How should I diagnose a VPN failure?",
    }


def test_generate_answer_rejects_empty_provider_response(monkeypatch) -> None:
    class FakeResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text="   ")

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm, "OpenAI", lambda api_key: FakeClient())

    with pytest.raises(llm.LLMProviderError):
        llm.generate_answer("How should I diagnose a VPN failure?")
