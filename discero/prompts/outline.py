"""Outline agent prompt."""
from __future__ import annotations

from ..tools import ResearchNote


SYSTEM = """You are a senior curriculum designer. You design structured, \
learnable courses for motivated self-study learners. You produce outlines \
that are neither shallow nor overwhelming: every chapter has a clear \
learning outcome, a realistic time estimate, and concrete topics.

You output JSON that exactly matches the provided schema — no extra fields, \
no missing fields. The course will be consumed by a downstream pipeline, so \
precision matters more than flourish."""


def user(
    *,
    title: str,
    subject: str,
    duration_weeks: int,
    difficulty: str,
    tone: str,
    research_notes: list[ResearchNote],
) -> str:
    # Target roughly 2 chapters / week, adjusted by difficulty.
    chapters_lo = max(duration_weeks, 1) * 2
    chapters_hi = chapters_lo + 2
    if difficulty == "advanced":
        chapters_lo = int(chapters_lo * 1.2)
        chapters_hi = int(chapters_hi * 1.2)

    notes_block = _format_notes(research_notes)

    return f"""Design a course outline.

TITLE: {title}
SUBJECT: {subject}
DURATION: {duration_weeks} weeks
DIFFICULTY: {difficulty}

TONE & STYLE: {tone}

REQUIREMENTS:
- Produce between {chapters_lo} and {chapters_hi} chapters. Each chapter is a \
coherent unit a learner can complete in one sitting.
- `estimatedHours` is the total estimated learner hours for the whole course.
- `learningObjectives` are 4–8 outcome statements for the *whole course*.
- `prerequisites` are concrete skills or knowledge the learner should already have.
- Each chapter's `learningGoals` are 3–5 outcomes specific to that chapter.
- Each chapter's `topics` are 4–8 concrete subjects covered.
- `gamePlan.weeklySchedule` has one entry per week ({duration_weeks} entries), \
mapping weeks to chapter indices (0-based).
- `gamePlan.milestones` are 2–4 checkpoint goals the learner should hit along the way.
- `gamePlan.assessmentStrategy` describes how the learner will know they've \
mastered the material (1–2 sentences).
- Do NOT include an `id` field on chapters — it will be assigned downstream.

RESEARCH NOTES (use as grounding; do not cite):
{notes_block}

Return a single JSON object matching the provided schema. No commentary."""


def _format_notes(notes: list[ResearchNote]) -> str:
    if not notes:
        return "(none available)"
    lines = []
    for i, n in enumerate(notes[:20], 1):
        src = n.get("source", "?")
        title = n.get("title", "")
        snippet = n.get("snippet", "")
        lines.append(f"{i}. [{src}] {title}\n   {snippet}")
    return "\n".join(lines)
