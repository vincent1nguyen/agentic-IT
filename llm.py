import os

from openai import OpenAI, OpenAIError


DEFAULT_MODEL = "gpt-5.6-luna"
SYSTEM_INSTRUCTIONS = """You assist IT technicians with troubleshooting.
Provide concise, practical diagnostic steps. Clearly state uncertainty and do not
claim that actions were performed. A technician must review the guidance before
acting on it."""


class LLMConfigurationError(RuntimeError):
    # docstring
    """Raised when the LLM provider is not configured."""


class LLMProviderError(RuntimeError):
    """Raised when the LLM provider cannot generate a response."""


def generate_answer(question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigurationError("OPENAI_API_KEY is not configured")

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=question,
        )
    except OpenAIError as exc:
        raise LLMProviderError("The AI provider request failed") from exc

    answer = response.output_text.strip()
    if not answer:
        raise LLMProviderError("The AI provider returned an empty response")

    return answer
