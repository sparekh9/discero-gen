"""Provider-agnostic LLM client protocol.

Every discero agent funnels through `LLMClient.structured_call`, which
takes a Pydantic response model and returns a parsed instance. Each
provider adapter (OpenAI, Anthropic, Gemini) implements this protocol
using its SDK's native structured-output primitive.
"""
from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMUnavailable(RuntimeError):
    """The selected provider's SDK isn't installed."""


class LLMRefusal(RuntimeError):
    """The model refused or returned no parseable output."""


@runtime_checkable
class LLMClient(Protocol):
    provider: str
    default_model: str
    default_mini_model: str

    def structured_call(
        self,
        *,
        model: str,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.4,
    ) -> T: ...
