"""Outline agent: research → course outline + game plan."""
from __future__ import annotations

from openai import OpenAI

from ..prompts import outline as prompt
from ..prompts.subject_configs import resolve
from ..schemas import CourseOutline
from ..tools import ResearchNote
from . import structured_call


def generate_outline(
    client: OpenAI,
    *,
    model: str,
    title: str,
    subject: str,
    duration_weeks: int,
    difficulty: str,
    research_notes: list[ResearchNote],
) -> CourseOutline:
    cfg = resolve(subject)
    user_msg = prompt.user(
        title=title,
        subject=subject,
        duration_weeks=duration_weeks,
        difficulty=difficulty,
        tone=cfg.tone,
        research_notes=research_notes,
    )
    return structured_call(
        client,
        model=model,
        system=prompt.SYSTEM,
        user=user_msg,
        response_model=CourseOutline,
        temperature=0.4,
    )
