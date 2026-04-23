"""Seminar agent (humanities only)."""
from __future__ import annotations

from openai import OpenAI

from ..prompts import seminar as prompt
from ..schemas import ChapterData, SeminarContent
from . import structured_call


def generate_seminar(
    client: OpenAI,
    *,
    model: str,
    course_title: str,
    subject: str,
    chapter: ChapterData,
) -> SeminarContent:
    user_msg = prompt.user(
        course_title=course_title,
        subject=subject,
        chapter=chapter,
    )
    return structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=user_msg,
        response_model=SeminarContent,
    )
