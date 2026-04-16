"""LangGraph pipeline state."""
from __future__ import annotations

from typing import Optional, TypedDict

from .schemas import CourseOutline, ImportedChapter


class PipelineState(TypedDict, total=False):
    # ── inputs ─────────────────────────────────────────────────────
    title: str
    subject: str
    duration_weeks: int
    difficulty: str  # "beginner" | "intermediate" | "advanced"
    use_research: bool
    model: str
    mini_model: str

    # ── intermediate artifacts ─────────────────────────────────────
    research_notes: list[dict]
    category: str  # stem | humanities | language | other
    is_humanities: bool
    outline: CourseOutline
    chapters: list[ImportedChapter]

    # ── progress / errors ──────────────────────────────────────────
    errors: list[str]
    progress_total_chapters: Optional[int]
