"""Seminar prompt (humanities only)."""
from __future__ import annotations

from ..schemas import ChapterData


SYSTEM = """You design Socratic seminars: structured debates where a \
learner argues against AI agents representing different schools of \
thought. You produce debate topics rooted in the chapter's material and \
agent viewpoints that embody coherent philosophical, historical, or \
ethical positions.

Each viewpoint must be defensible in good faith — no strawmen. Assign \
stable `id` strings (slug-like: lowercase, hyphens). The learner will \
pick a topic and 2–3 viewpoints to debate against.

Output JSON matching the provided schema exactly."""


def user(
    *,
    course_title: str,
    subject: str,
    chapter: ChapterData,
) -> str:
    topics = "\n".join(f"- {t}" for t in chapter.topics)
    return f"""Design seminar content for this chapter.

COURSE: {course_title}
SUBJECT: {subject}
CHAPTER: {chapter.title}
DESCRIPTION: {chapter.description}

TOPICS COVERED:
{topics}

REQUIREMENTS:
- `topics`: 2–3 debate topics. Each has:
    - `id` (slug)
    - `title`
    - `context`: 2–3 sentence framing
    - `centralQuestion`: the core question being debated
    - `relevantConcepts`: 3–5 concepts from the chapter
    - `suggestedViewpoints`: 2–4 viewpoint ids (must match `viewpoints[].id`)
    - `difficulty`: beginner | intermediate | advanced
- `viewpoints`: 3–5 agent viewpoints. Each has:
    - `id` (slug, unique, referenced by topics)
    - `name` (e.g. "Utilitarian Pragmatist")
    - `description`: 1–2 sentences on the position
    - `historicalFigure` (optional): a representative thinker
    - `keyPrinciples`: 3–5 bullets
    - `typicalArguments`: 3–5 sample arguments this agent would make
    - `rhetoricStyle`: how the agent argues (e.g. "analytical, citation-heavy")

Return a single JSON object. No commentary."""
