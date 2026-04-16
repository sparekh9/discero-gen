"""LangGraph wiring for the discero pipeline.

Flow:

    research → outline → chapter_loop → [humanities?] → seminar → finalize
                                              │
                                              └── no → finalize
"""
from __future__ import annotations

from openai import OpenAI

from langgraph.graph import END, START, StateGraph

from . import progress
from .agents.chapter import generate_chapter_content
from .agents.flashcards import generate_flashcards
from .agents.outline import generate_outline
from .agents.quiz import generate_quiz
from .agents.seminar import generate_seminar
from .prompts.subject_configs import resolve
from .schemas import ImportedChapter
from .state import PipelineState
from .tools import ResearchNote, ToolUnavailable
from .tools import arxiv as arxiv_tool
from .tools import tavily as tavily_tool
from .tools import wikipedia as wiki_tool


# ── Node implementations ─────────────────────────────────────────────

def _research_node_factory(client: OpenAI, tavily_key: str):
    def research(state: PipelineState) -> PipelineState:
        if not state.get("use_research", True):
            progress.info("research skipped (--no-research)")
            return {"research_notes": [], "category": resolve(state["subject"]).category}

        title = state["title"]
        subject = state["subject"]
        query = f"{title} ({subject})"
        notes: list[ResearchNote] = []

        with progress.stage(1, "research"):
            for name, runner in (
                ("wikipedia", lambda: wiki_tool.search(query, max_results=4)),
                ("arxiv", lambda: arxiv_tool.search(query, max_results=4)),
                ("tavily", lambda: tavily_tool.search(query, tavily_key, max_results=5)),
            ):
                try:
                    got = runner()
                    notes.extend(got)
                    progress.info(f"  {name}: {len(got)} notes")
                except ToolUnavailable as e:
                    progress.warn(f"{name} unavailable: {e}")

        # Dedupe by (source, title).
        seen: set[tuple[str, str]] = set()
        deduped: list[ResearchNote] = []
        for n in notes:
            key = (n.get("source", ""), n.get("title", ""))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(n)

        return {
            "research_notes": deduped[:20],
            "category": resolve(subject).category,
            "is_humanities": resolve(subject).category == "humanities",
        }

    return research


def _outline_node_factory(client: OpenAI):
    def outline(state: PipelineState) -> PipelineState:
        with progress.stage(2, "outline"):
            result = generate_outline(
                client,
                model=state["model"],
                title=state["title"],
                subject=state["subject"],
                duration_weeks=state["duration_weeks"],
                difficulty=state["difficulty"],
                research_notes=state.get("research_notes", []),
            )
        progress.info(f"  outline: {len(result.chapters)} chapters, {result.estimatedHours}h")
        return {
            "outline": result,
            "progress_total_chapters": len(result.chapters),
        }

    return outline


def _chapters_node_factory(client: OpenAI):
    def chapters(state: PipelineState) -> PipelineState:
        outline = state["outline"]
        total = len(outline.chapters)
        built: list[ImportedChapter] = []

        progress.log(3, f"chapters (0/{total})")
        for i, ch in enumerate(outline.chapters):
            ch_with_id = ch.model_copy(update={"id": i})
            content = generate_chapter_content(
                client,
                model=state["model"],
                course_title=outline.title,
                course_description=outline.description,
                subject=state["subject"],
                chapter_index=i,
                total_chapters=total,
                chapter=ch_with_id,
            )
            cards = generate_flashcards(
                client,
                model=state["mini_model"],
                chapter=ch_with_id,
                content=content,
            )
            quiz = generate_quiz(
                client,
                model=state["mini_model"],
                chapter=ch_with_id,
                content=content,
            )
            built.append(
                ImportedChapter(
                    index=i,
                    chapterData=ch_with_id,
                    content=content,
                    flashcards=cards,
                    quiz=quiz,
                )
            )
            progress.log(3, f"chapters ({i + 1}/{total})", ch.title[:60])

        return {"chapters": built}

    return chapters


def _seminar_node_factory(client: OpenAI):
    def seminar(state: PipelineState) -> PipelineState:
        chapters = list(state.get("chapters", []))
        total = len(chapters)
        outline = state["outline"]
        progress.log(4, f"seminars (0/{total})")
        for i, ch in enumerate(chapters):
            content = generate_seminar(
                client,
                model=state["model"],
                course_title=outline.title,
                subject=state["subject"],
                chapter=ch.chapterData,
            )
            chapters[i] = ch.model_copy(update={"seminar": content})
            progress.log(4, f"seminars ({i + 1}/{total})", ch.chapterData.title[:60])
        return {"chapters": chapters}

    return seminar


def _finalize_node(state: PipelineState) -> PipelineState:
    progress.log(5, "validating & writing")
    return {}


def _route_after_chapters(state: PipelineState) -> str:
    return "seminar" if state.get("is_humanities") else "finalize"


# ── Public: compile the graph ─────────────────────────────────────────

def build_graph(client: OpenAI, tavily_key: str):
    g: StateGraph = StateGraph(PipelineState)
    g.add_node("research", _research_node_factory(client, tavily_key))
    g.add_node("outline", _outline_node_factory(client))
    g.add_node("chapters", _chapters_node_factory(client))
    g.add_node("seminar", _seminar_node_factory(client))
    g.add_node("finalize", _finalize_node)

    g.add_edge(START, "research")
    g.add_edge("research", "outline")
    g.add_edge("outline", "chapters")
    g.add_conditional_edges(
        "chapters",
        _route_after_chapters,
        {"seminar": "seminar", "finalize": "finalize"},
    )
    g.add_edge("seminar", "finalize")
    g.add_edge("finalize", END)

    return g.compile()
