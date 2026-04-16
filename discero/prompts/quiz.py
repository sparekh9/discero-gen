"""Quiz prompt."""
from __future__ import annotations

from ..schemas import ChapterContent, ChapterData


SYSTEM = """You generate multiple-choice quiz questions that test \
understanding, not recall of trivia. Every question has exactly one \
correct answer and 3 plausible distractors. The `correct` field is the \
zero-based index of the correct option. Explanations should teach — \
they explain *why* the right answer is right and, briefly, why the \
distractors are wrong.

Output JSON matching the provided schema exactly."""


def user(
    *,
    chapter: ChapterData,
    content: ChapterContent,
) -> str:
    goals = "\n".join(f"- {g}" for g in chapter.learningGoals)
    return f"""Generate 5–8 quiz questions for this chapter.

CHAPTER: {chapter.title}
LEARNING GOALS:
{goals}

SUMMARY OF CONTENT: {content.summary}

REQUIREMENTS:
- 5–8 multiple-choice questions.
- Exactly 4 options per question.
- `correct` is the zero-based index (0..3) of the correct option.
- `explanation` is 2–3 sentences teaching the reasoning.
- Prefer questions that require reasoning, not memorization.

Return a JSON object with a `quiz` array."""
