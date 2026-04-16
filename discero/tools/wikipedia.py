"""Wikipedia lookup, disambiguation-safe."""
from __future__ import annotations

from . import ResearchNote, ToolUnavailable


def search(query: str, max_results: int = 4) -> list[ResearchNote]:
    try:
        import wikipedia  # type: ignore
    except ImportError as e:
        raise ToolUnavailable(f"wikipedia not installed: {e}") from e

    notes: list[ResearchNote] = []
    try:
        titles = wikipedia.search(query, results=max_results)
    except Exception as e:  # noqa: BLE001
        raise ToolUnavailable(f"wikipedia search failed: {e}") from e

    for title in titles:
        try:
            page = wikipedia.page(title, auto_suggest=False, redirect=True)
        except wikipedia.DisambiguationError as e:  # type: ignore[attr-defined]
            # Pick the first disambiguation option that resolves cleanly.
            if not e.options:
                continue
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False, redirect=True)
            except Exception:
                continue
        except wikipedia.PageError:  # type: ignore[attr-defined]
            continue
        except Exception:  # noqa: BLE001
            continue

        try:
            summary = wikipedia.summary(page.title, sentences=3, auto_suggest=False)
        except Exception:  # noqa: BLE001
            summary = ""

        notes.append(
            ResearchNote(
                source="wikipedia",
                title=page.title,
                snippet=summary[:800],
                url=page.url,
            )
        )
    return notes
