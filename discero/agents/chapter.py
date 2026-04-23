"""Chapter content agent."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from openai import OpenAI

from ..prompts import chapter as prompt
from ..prompts.subject_configs import resolve
from ..schemas import ChapterContent, ChapterData, ContentSection, Exercise
from . import structured_call


class _ChapterBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    introduction: str
    sections: list[ContentSection]
    summary: str
    nextSteps: str


class _ChapterExercises(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exercises: list[Exercise]


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
    body = structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=prompt.user(
            course_title=course_title,
            course_description=course_description,
            subject=subject,
            tone=cfg.tone,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            chapter=chapter,
        ),
        response_model=_ChapterBody,
    )
    partial_content = ChapterContent(
        introduction=body.introduction,
        sections=body.sections,
        exercises=[],
        summary=body.summary,
        nextSteps=body.nextSteps,
    )
    exercises_result = structured_call(
        client,
        model=model,
        system=prompt.SYSTEM_EXERCISES,
        user=prompt.user_exercises(chapter=chapter, content=partial_content),
        response_model=_ChapterExercises,
    )
    return ChapterContent(
        introduction=body.introduction,
        sections=body.sections,
        exercises=exercises_result.exercises,
        summary=body.summary,
        nextSteps=body.nextSteps,
    )
