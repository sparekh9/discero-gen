"""OpenAI adapter using `client.beta.chat.completions.parse`."""
from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from .base import LLMRefusal, LLMUnavailable

T = TypeVar("T", bound=BaseModel)


class OpenAIClient:
    provider = "openai"
    default_model = "gpt-4o-2024-08-06"
    default_mini_model = "gpt-4o-mini"

    def __init__(self, api_key: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise LLMUnavailable(
                "openai SDK not installed. run: pip install openai"
            ) from e
        self._client = OpenAI(api_key=api_key)

    def structured_call(
        self,
        *,
        model: str,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.4,
    ) -> T:
        completion = self._client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=response_model,
            temperature=temperature,
        )
        choice = completion.choices[0].message
        if choice.parsed is None:
            raise LLMRefusal(
                f"openai returned no parsed output: {choice.refusal}"
            )
        return choice.parsed
