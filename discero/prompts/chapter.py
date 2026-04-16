"""Chapter content agent prompt."""
from __future__ import annotations

from ..schemas import ChapterData


SYSTEM = """You are writing chapter content for a self-study course. You \
write like a patient, rigorous tutor: explain intuitions first, then \
formalize. Every section should teach something concrete, include worked \
examples where applicable, and end with clear key points the learner can \
hold onto.

Escape LaTeX carefully — in JSON, backslashes must be doubled. Use inline \
math $...$ and display math $$...$$ for STEM content. For humanities and \
other subjects, prefer prose.

Output JSON matching the provided schema exactly."""


def user(
    *,
    course_title: str,
    course_description: str,
    subject: str,
    tone: str,
    chapter_index: int,
    total_chapters: int,
    chapter: ChapterData,
) -> str:
    goals = "\n".join(f"- {g}" for g in chapter.learningGoals)
    topics = "\n".join(f"- {t}" for t in chapter.topics)
    return f"""Write the full content for chapter {chapter_index + 1} of {total_chapters}.

COURSE: {course_title}
COURSE DESCRIPTION: {course_description}
SUBJECT: {subject}
TONE: {tone}

CHAPTER TITLE: {chapter.title}
CHAPTER DESCRIPTION: {chapter.description}
ESTIMATED TIME: {chapter.estimatedTime}

LEARNING GOALS:
{goals}

TOPICS TO COVER:
{topics}

REQUIREMENTS:
- `introduction`: 2–3 paragraphs hooking the learner and framing the chapter.
- `sections`: 3–6 sections. Each section has:
    - `title`
    - `content`: 3–6 paragraphs of substantive explanation
    - `examples`: 2–4 concrete examples (short strings, not full paragraphs)
    - `keyPoints`: 3–5 takeaway bullets
- `exercises`: 3–6 exercises spanning types (practice, quiz, reflection) \
and difficulties (easy, medium, hard). Each has a clear `question`, a full \
`solution`, and a difficulty label.
- `summary`: one paragraph tying the chapter together.
- `nextSteps`: 1–2 sentences on what to do next.

Return a single JSON object. No commentary."""
