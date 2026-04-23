"""Flashcards agent."""
from __future__ import annotations

from openai import OpenAI
from pydantic import BaseModel, ConfigDict

from ..prompts import flashcards as prompt
from ..schemas import ChapterContent, ChapterData, Flashcard
from . import structured_call


class _FlashcardsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    flashcards: list[Flashcard]


def generate_flashcards(
    client: OpenAI,
    *,
    model: str,
    chapter: ChapterData,
    content: ChapterContent,
) -> list[Flashcard]:
    user_msg = prompt.user(chapter=chapter, content=content)
    result = structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=user_msg,
        response_model=_FlashcardsEnvelope,
    )
    return result.flashcards
