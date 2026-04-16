"""Pydantic mirror of Discero's schema.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from . import SCHEMA_VERSION


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ── Outline ────────────────────────────────────────────────────────────

class WeeklyPlan(_StrictModel):
    week: int
    focus: str
    chapters: list[int]
    activities: list[str]


class Milestone(_StrictModel):
    week: int
    title: str
    description: str
    deliverable: str


class GamePlan(_StrictModel):
    weeklySchedule: list[WeeklyPlan]
    milestones: list[Milestone]
    assessmentStrategy: str


class ChapterData(_StrictModel):
    id: Optional[int] = None
    title: str
    description: str
    estimatedTime: str
    learningGoals: list[str]
    topics: list[str]


class CourseOutline(_StrictModel):
    title: str
    description: str
    learningObjectives: list[str]
    prerequisites: list[str]
    estimatedHours: float
    chapters: list[ChapterData] = Field(min_length=1)
    gamePlan: GamePlan


# ── Chapter content ────────────────────────────────────────────────────

class ContentSection(_StrictModel):
    title: str
    content: str
    examples: list[str]
    keyPoints: list[str]


class Exercise(_StrictModel):
    type: Literal["practice", "quiz", "reflection"]
    question: str
    solution: str
    difficulty: Literal["easy", "medium", "hard"]


class ChapterContent(_StrictModel):
    introduction: str
    sections: list[ContentSection]
    exercises: list[Exercise]
    summary: str
    nextSteps: str


class Flashcard(_StrictModel):
    front: str
    back: str


class QuizQuestion(_StrictModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct: int = Field(ge=0)
    explanation: str


# ── Seminar (humanities) ───────────────────────────────────────────────

class AgentViewpoint(_StrictModel):
    id: str
    name: str
    description: str
    historicalFigure: Optional[str] = None
    keyPrinciples: list[str]
    typicalArguments: list[str]
    rhetoricStyle: str


class DebateTopic(_StrictModel):
    id: str
    title: str
    context: str
    centralQuestion: str
    relevantConcepts: list[str]
    suggestedViewpoints: list[str]
    difficulty: Literal["beginner", "intermediate", "advanced"]


class SeminarContent(_StrictModel):
    topics: list[DebateTopic]
    viewpoints: list[AgentViewpoint]


# ── Full imported chapter ──────────────────────────────────────────────

class ImportedChapter(_StrictModel):
    index: int = Field(ge=0)
    chapterData: ChapterData
    content: ChapterContent
    flashcards: list[Flashcard]
    quiz: list[QuizQuestion]
    seminar: Optional[SeminarContent] = None


# ── Top-level payload ──────────────────────────────────────────────────

class CourseBody(_StrictModel):
    subject: str = Field(min_length=1)
    duration: int = Field(ge=1)
    outline: CourseOutline
    chapters: list[ImportedChapter] = Field(min_length=1)


class CoursePayload(_StrictModel):
    schemaVersion: Literal[1] = SCHEMA_VERSION  # type: ignore[assignment]
    generatedBy: str
    generatedAt: str
    course: CourseBody
