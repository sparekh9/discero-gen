"""Chapter content agent prompts."""
from __future__ import annotations

from ..schemas import ChapterContent, ChapterData


SYSTEM = """You are writing chapter content for a self-study course. You \
write like a patient, rigorous tutor: explain intuitions first, then \
formalize. Every section should teach something concrete, include worked \
examples where applicable, and end with clear key points the learner can \
hold onto.

Escape LaTeX carefully — in JSON, backslashes must be doubled. Use inline \
math $...$ and display math $$...$$ for STEM content. For humanities and \
other subjects, prefer prose. NEVER use \\(...\\) or \\[...\\] delimiters — \
only $ and $$ are supported by the renderer.

Every math technique introduced must be demonstrated with a complete \
step-by-step worked example: state the problem, show each transformation on \
its own line with a brief annotation, and state the result. Never name a \
technique without immediately demonstrating it.

Output JSON matching the provided schema exactly."""


SYSTEM_EXERCISES = """You are generating exercises for a self-study course \
chapter. Exercises span practice, quiz, and reflection types across easy, \
medium, and hard difficulties. Each exercise has a clear question and a \
complete solution.

Escape LaTeX carefully — in JSON, backslashes must be doubled. Use inline \
math $...$ and display math $$...$$ for STEM content. NEVER use \\(...\\) or \
\\[...\\] delimiters — only $ and $$ are supported by the renderer. Math in \
`question` and `solution` must be wrapped in $ or $$ — never bare LaTeX.

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
    - `content`: 3–6 paragraphs of substantive explanation; any math \
technique must include a step-by-step worked example inline
    - `examples`: 2–4 concrete examples (short strings, not full paragraphs); \
math expressions must be wrapped in $ or $$ — never bare LaTeX
    - `keyPoints`: 3–5 takeaway bullets; math expressions must be wrapped in $ or $$ — never bare LaTeX
- `summary`: one paragraph tying the chapter together.
- `nextSteps`: 1–2 sentences on what to do next.

Return a single JSON object. No commentary."""


def user_exercises(
    *,
    chapter: ChapterData,
    content: ChapterContent,
) -> str:
    goals = "\n".join(f"- {g}" for g in chapter.learningGoals)
    key_points = []
    for section in content.sections:
        key_points.extend(section.keyPoints)
    kp_block = "\n".join(f"- {k}" for k in key_points[:20])
    return f"""Generate exercises for this chapter.

CHAPTER: {chapter.title}
LEARNING GOALS:
{goals}

SUMMARY: {content.summary}

KEY POINTS COVERED:
{kp_block}

REQUIREMENTS:
- 3–6 exercises spanning types (practice, quiz, reflection) and \
difficulties (easy, medium, hard).
- Each exercise has a clear `question`, a full step-by-step `solution`, \
and a `difficulty` label.
- `type` must be one of: practice, quiz, reflection.
- `difficulty` must be one of: easy, medium, hard.

Return a JSON object with an `exercises` array. No commentary."""
