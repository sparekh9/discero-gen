"""Subject → category routing and tone hints."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubjectConfig:
    category: str  # stem | humanities | language | other
    tone: str
    research_weight: dict[str, float]  # source → weight


_HUMANITIES = {
    "history", "philosophy", "literature", "art", "ethics",
    "religion", "politics", "political science", "law",
    "sociology", "anthropology", "classics", "theology",
}

_STEM = {
    "math", "mathematics", "physics", "chemistry", "biology",
    "computer science", "cs", "programming", "engineering",
    "statistics", "data science", "machine learning", "ml",
    "astronomy", "geology", "neuroscience",
}

_LANGUAGE = {
    "spanish", "french", "german", "mandarin", "japanese",
    "korean", "latin", "greek", "italian", "portuguese",
    "arabic", "hindi", "russian", "english",
}

_DEFAULT = SubjectConfig(
    category="other",
    tone="Clear, engaging, and grounded in concrete examples.",
    research_weight={"wikipedia": 1.0, "tavily": 1.0, "arxiv": 0.5},
)

_STEM_CONFIG = SubjectConfig(
    category="stem",
    tone=(
        "Rigorous and precise. Derive before you assert. Use worked examples "
        "and, where helpful, LaTeX (wrap inline math in $...$ and display math "
        "in $$...$$). Favor intuition first, then formalism."
    ),
    research_weight={"arxiv": 1.2, "wikipedia": 1.0, "tavily": 0.8},
)

_HUMANITIES_CONFIG = SubjectConfig(
    category="humanities",
    tone=(
        "Analytical and interpretive. Contextualize arguments historically. "
        "Present multiple perspectives fairly and encourage the learner to "
        "form their own view through evidence."
    ),
    research_weight={"wikipedia": 1.2, "tavily": 1.0, "arxiv": 0.3},
)

_LANGUAGE_CONFIG = SubjectConfig(
    category="language",
    tone=(
        "Practical and communicative. Mix grammar explanations with usable "
        "dialogues. Introduce vocabulary in context and reinforce via drills."
    ),
    research_weight={"wikipedia": 1.0, "tavily": 1.0, "arxiv": 0.2},
)


def resolve(subject: str) -> SubjectConfig:
    s = subject.strip().lower()
    if s in _HUMANITIES:
        return _HUMANITIES_CONFIG
    if s in _STEM:
        return _STEM_CONFIG
    if s in _LANGUAGE:
        return _LANGUAGE_CONFIG
    # Loose substring fallback.
    for kw in _HUMANITIES:
        if kw in s:
            return _HUMANITIES_CONFIG
    for kw in _STEM:
        if kw in s:
            return _STEM_CONFIG
    for kw in _LANGUAGE:
        if kw in s:
            return _LANGUAGE_CONFIG
    return _DEFAULT


def is_humanities(subject: str) -> bool:
    return resolve(subject).category == "humanities"
