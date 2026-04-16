"""Gemini adapter using `google-genai` with Pydantic `response_schema`."""
from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ValidationError

from .base import LLMRefusal, LLMUnavailable

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    provider = "gemini"
    default_model = "gemini-2.5-pro"
    default_mini_model = "gemini-2.5-flash"

    def __init__(self, api_key: str) -> None:
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError as e:
            raise LLMUnavailable(
                "google-genai SDK not installed. run: pip install 'discero-gen[google]'"
            ) from e
        self._client = genai.Client(api_key=api_key)
        self._types = genai_types

    def structured_call(
        self,
        *,
        model: str,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.4,
    ) -> T:
        config = self._types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_model,
        )
        response = self._client.models.generate_content(
            model=model,
            contents=user,
            config=config,
        )

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, response_model):
            return parsed

        text = getattr(response, "text", None)
        if not text:
            raise LLMRefusal("gemini returned no text")
        try:
            return response_model.model_validate_json(text)
        except ValidationError as e:
            raise LLMRefusal(
                f"gemini returned invalid {response_model.__name__}: {e}"
            ) from e
