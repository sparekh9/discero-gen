"""Tavily web search, gated on TAVILY_API_KEY."""
from __future__ import annotations

from . import ResearchNote, ToolUnavailable


def search(query: str, api_key: str, max_results: int = 5) -> list[ResearchNote]:
    if not api_key:
        raise ToolUnavailable("TAVILY_API_KEY not set")

    try:
        from tavily import TavilyClient  # type: ignore
    except ImportError as e:
        raise ToolUnavailable(f"tavily-python not installed: {e}") from e

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )
    except Exception as e:  # noqa: BLE001 - network/auth/etc. all fail the tool
        raise ToolUnavailable(f"tavily call failed: {e}") from e

    notes: list[ResearchNote] = []
    for r in response.get("results", []):
        notes.append(
            ResearchNote(
                source="tavily",
                title=r.get("title", "")[:200],
                snippet=r.get("content", "")[:800],
                url=r.get("url"),
            )
        )
    return notes
