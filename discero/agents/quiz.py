"""Quiz agent."""
from __future__ import annotations

from openai import OpenAI
from pydantic import BaseModel, ConfigDict

from ..prompts import quiz as prompt
from ..schemas import ChapterContent, ChapterData, QuizQuestion
from . import structured_call


class _QuizEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quiz: list[QuizQuestion]


def generate_quiz(
    client: OpenAI,
    *,
    model: str,
    chapter: ChapterData,
    content: ChapterContent,
) -> list[QuizQuestion]:
    user_msg = prompt.user(chapter=chapter, content=content)
    result = structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=user_msg,
        response_model=_QuizEnvelope,
        temperature=0.3,
    )
    return result.quiz
