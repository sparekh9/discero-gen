"""Shared helpers for structured-output OpenAI calls.

Uses the v1 SDK's `client.beta.chat.completions.parse` with a Pydantic
`response_format`, which gives us a parsed Pydantic instance directly
and raises on schema mismatch. No hand-written JSON schemas, no manual
parse-and-retry logic.
"""
from __future__ import annotations

from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


def structured_call(
    client: OpenAI,
    *,
    model: str,
    system: str,
    user: str,
    response_model: type[T],
) -> T:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format=response_model,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        refusal = completion.choices[0].message.refusal
        raise RuntimeError(f"model refused or returned no parsed output: {refusal}")
    return parsed
