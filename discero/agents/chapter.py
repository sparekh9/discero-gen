"""Chapter content agent."""
from __future__ import annotations

from openai import OpenAI

from ..prompts import chapter as prompt
from ..prompts.subject_configs import resolve
from ..schemas import ChapterContent, ChapterData
from . import structured_call


def generate_chapter_content(
    client: OpenAI,
    *,
    model: str,
    course_title: str,
    course_description: str,
    subject: str,
    chapter_index: int,
    total_chapters: int,
    chapter: ChapterData,
) -> ChapterContent:
    cfg = resolve(subject)
    user_msg = prompt.user(
        course_title=course_title,
        course_description=course_description,
        subject=subject,
        tone=cfg.tone,
        chapter_index=chapter_index,
        total_chapters=total_chapters,
        chapter=chapter,
    )
    return structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=user_msg,
        response_model=ChapterContent,
        temperature=0.5,
    )
