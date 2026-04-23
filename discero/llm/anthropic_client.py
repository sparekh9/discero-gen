"""Anthropic adapter using forced tool-use for schema-guaranteed JSON.

Anthropic's canonical way to get a structured object is to define a
single tool whose `input_schema` is the Pydantic model's JSON schema,
and force the model to call it via `tool_choice`.
"""
from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .base import LLMRefusal, LLMUnavailable

T = TypeVar("T", bound=BaseModel)

_MAX_TOKENS = 8192
_TOOL_NAME = "emit_structured_output"


def _clean_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Strip JSON-schema features Anthropic's tool_use rejects.

    Anthropic is stricter than OpenAI: it rejects `$defs`/`$ref`, `title`,
    `default`, and a few other Pydantic-default fields. We inline refs
    and drop the noisy metadata.
    """
    defs = schema.get("$defs", {}) or schema.get("definitions", {})

    def inline(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node and len(node) == 1:
                ref = node["$ref"]
                name = ref.rsplit("/", 1)[-1]
                target = defs.get(name, {})
                return inline(target)
            return {
                k: inline(v)
                for k, v in node.items()
                if k not in {"title", "default", "$defs", "definitions"}
            }
        if isinstance(node, list):
            return [inline(x) for x in node]
        return node

    cleaned = inline(schema)
    if isinstance(cleaned, dict):
        cleaned.pop("$defs", None)
        cleaned.pop("definitions", None)
    return cleaned


class AnthropicClient:
    provider = "anthropic"
    default_model = "claude-sonnet-4-5"
    default_mini_model = "claude-haiku-4-5-20251001"

    def __init__(self, api_key: str) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise LLMUnavailable(
                "anthropic SDK not installed. run: pip install 'discero-gen[anthropic]'"
            ) from e
        self._client = Anthropic(api_key=api_key)

    def structured_call(
        self,
        *,
        model: str,
        system: str,
        user: str,
        response_model: type[T],
    ) -> T:
        schema = _clean_schema(response_model.model_json_schema())

        response = self._client.messages.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            tools=[
                {
                    "name": _TOOL_NAME,
                    "description": (
                        f"Return a {response_model.__name__} object. "
                        "You MUST call this tool with valid arguments."
                    ),
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
        )

        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == _TOOL_NAME:
                try:
                    return response_model.model_validate(block.input)
                except ValidationError as e:
                    raise LLMRefusal(
                        f"anthropic returned invalid {response_model.__name__}: {e}"
                    ) from e

        raise LLMRefusal(
            f"anthropic did not call {_TOOL_NAME}; stop_reason={response.stop_reason}"
        )
