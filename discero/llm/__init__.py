"""Provider-agnostic LLM layer for discero.

Usage:

    from discero.llm import build_llm_client
    client = build_llm_client("anthropic", api_key=...)
    result = client.structured_call(
        model="claude-sonnet-4-5",
        system="...",
        user="...",
        response_model=MyPydanticModel,
    )
"""
from __future__ import annotations

from .base import LLMClient, LLMRefusal, LLMUnavailable

SUPPORTED_PROVIDERS: tuple[str, ...] = ("openai", "anthropic", "gemini")


def build_llm_client(provider: str, api_key: str) -> LLMClient:
    p = provider.lower().strip()
    if p == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient(api_key)
    if p == "anthropic":
        from .anthropic_client import AnthropicClient
        return AnthropicClient(api_key)
    if p == "gemini":
        from .gemini_client import GeminiClient
        return GeminiClient(api_key)
    raise ValueError(
        f"unknown provider: {provider!r} (expected one of: {', '.join(SUPPORTED_PROVIDERS)})"
    )


def default_models_for(provider: str) -> tuple[str, str]:
    """Return (primary, mini) default model names for a provider."""
    p = provider.lower().strip()
    if p == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient.default_model, OpenAIClient.default_mini_model
    if p == "anthropic":
        from .anthropic_client import AnthropicClient
        return AnthropicClient.default_model, AnthropicClient.default_mini_model
    if p == "gemini":
        from .gemini_client import GeminiClient
        return GeminiClient.default_model, GeminiClient.default_mini_model
    raise ValueError(f"unknown provider: {provider!r}")


__all__ = [
    "LLMClient",
    "LLMRefusal",
    "LLMUnavailable",
    "SUPPORTED_PROVIDERS",
    "build_llm_client",
    "default_models_for",
]
