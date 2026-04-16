"""arXiv top-k search."""
from __future__ import annotations

from . import ResearchNote, ToolUnavailable


def search(query: str, max_results: int = 4) -> list[ResearchNote]:
    try:
        import arxiv  # type: ignore
    except ImportError as e:
        raise ToolUnavailable(f"arxiv not installed: {e}") from e

    try:
        client = arxiv.Client()
        search_obj = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = list(client.results(search_obj))
    except Exception as e:  # noqa: BLE001
        raise ToolUnavailable(f"arxiv call failed: {e}") from e

    notes: list[ResearchNote] = []
    for r in results:
        notes.append(
            ResearchNote(
                source="arxiv",
                title=r.title.strip()[:200],
                snippet=(r.summary or "").replace("\n", " ").strip()[:800],
                url=r.entry_id,
            )
        )
    return notes
