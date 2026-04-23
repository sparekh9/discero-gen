"""Flashcards prompt."""
from __future__ import annotations

from ..schemas import ChapterContent, ChapterData


SYSTEM = """You generate spaced-repetition flashcards. Each card tests one \
fact or concept. Fronts are questions or prompts; backs are concise, \
correct answers. No multi-part cards, no trivia. For math, use only $ and \
$$ delimiters — never \\(...\\) or \\[...\\].

Output JSON matching the provided schema exactly."""


def user(
    *,
    chapter: ChapterData,
    content: ChapterContent,
) -> str:
    key_points = []
    for section in content.sections:
        key_points.extend(section.keyPoints)
    kp_block = "\n".join(f"- {k}" for k in key_points[:30])
    return f"""Generate 8–12 flashcards for this chapter.

CHAPTER: {chapter.title}
DESCRIPTION: {chapter.description}

KEY POINTS ALREADY COVERED:
{kp_block}

REQUIREMENTS:
- 8–12 cards total.
- Cover the most important facts, definitions, and relationships.
- One concept per card.
- Fronts are short (1 sentence); backs are concise but complete.

Return a JSON object with a `flashcards` array."""
