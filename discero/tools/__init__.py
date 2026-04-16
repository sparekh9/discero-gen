"""Research tools: Tavily (optional), Wikipedia, arXiv.

Each tool returns a uniform `ResearchNote` dict:

    { "source": str, "title": str, "snippet": str, "url": str | None }

so the outline agent can splice them into a prompt without caring where
they came from.
"""
from __future__ import annotations

from typing import TypedDict


class ResearchNote(TypedDict, total=False):
    source: str  # "tavily" | "wikipedia" | "arxiv"
    title: str
    snippet: str
    url: str | None


class ToolUnavailable(RuntimeError):
    """Raised when a tool can't run (missing key, network error, etc.)."""
