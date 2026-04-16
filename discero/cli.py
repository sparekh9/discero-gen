"""Typer CLI entry point for discero."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from openai import OpenAI
from pydantic import ValidationError

from . import GENERATED_BY, __version__
from .config import load_settings
from .graph import build_graph
from .output import build_payload, format_validation_error, validate_file, write_payload
from .progress import error, info, warn
from .state import PipelineState


app = typer.Typer(
    add_completion=False,
    help="Agentic course generator for l2l. Produces a course.json you upload to the web app.",
)


@app.command()
def create(
    title: str = typer.Option(..., "--title", help="Course title"),
    subject: str = typer.Option(..., "--subject", help="Subject (free text, e.g. 'history', 'math')"),
    duration: int = typer.Option(..., "--duration", min=1, help="Course length in weeks"),
    difficulty: str = typer.Option(
        "intermediate",
        "--difficulty",
        help="beginner | intermediate | advanced",
    ),
    out: Path = typer.Option(Path("./course.json"), "--out", help="Output path"),
    model: str | None = typer.Option(None, "--model", help="Primary model override"),
    mini_model: str | None = typer.Option(None, "--mini-model", help="Mini model override (flashcards, quiz)"),
    no_research: bool = typer.Option(False, "--no-research", help="Skip the research stage"),
) -> None:
    """Generate a course.json locally."""
    settings = load_settings()

    if not settings.openai_api_key:
        error("OPENAI_API_KEY is not set. Put it in .env or export it in your shell.")
        raise typer.Exit(code=2)

    if difficulty not in {"beginner", "intermediate", "advanced"}:
        error(f"--difficulty must be one of beginner|intermediate|advanced, got '{difficulty}'")
        raise typer.Exit(code=2)

    if not settings.tavily_api_key:
        warn("TAVILY_API_KEY not set — Tavily disabled, using Wikipedia + arXiv only.")

    chosen_model = model or settings.discero_model
    chosen_mini = mini_model or settings.discero_mini_model

    info(f"discero {__version__} — generating '{title}' ({subject}, {duration}w, {difficulty})")
    info(f"primary model: {chosen_model}   mini model: {chosen_mini}")

    client = OpenAI(api_key=settings.openai_api_key)
    graph = build_graph(client, settings.tavily_api_key)

    initial: PipelineState = {
        "title": title,
        "subject": subject,
        "duration_weeks": duration,
        "difficulty": difficulty,
        "use_research": not no_research,
        "model": chosen_model,
        "mini_model": chosen_mini,
    }

    try:
        final_state: PipelineState = graph.invoke(initial)  # type: ignore[assignment]
    except Exception as e:  # noqa: BLE001
        error(f"pipeline failed: {e}")
        raise typer.Exit(code=1)

    try:
        payload = build_payload(final_state)
    except ValidationError as e:
        error(format_validation_error(e))
        raise typer.Exit(code=1)
    except Exception as e:  # noqa: BLE001
        error(f"could not assemble payload: {e}")
        raise typer.Exit(code=1)

    write_payload(payload, out)
    info(f"wrote {out} ({len(payload.course.chapters)} chapters)")
    typer.echo(str(out))


@app.command()
def validate(path: Path = typer.Argument(..., exists=True, readable=True, help="Path to course.json")) -> None:
    """Validate a course.json without calling the model."""
    try:
        payload = validate_file(path)
    except ValidationError as e:
        error(format_validation_error(e))
        raise typer.Exit(code=1)
    except json.JSONDecodeError as e:
        error(f"invalid JSON: {e}")
        raise typer.Exit(code=1)

    info(
        f"OK — {payload.course.outline.title} "
        f"({payload.course.subject}, {len(payload.course.chapters)} chapters, "
        f"schemaVersion={payload.schemaVersion}, generatedBy={payload.generatedBy})"
    )


@app.command()
def version() -> None:
    """Print discero version."""
    typer.echo(GENERATED_BY)


def main() -> None:  # pragma: no cover - entry point
    app()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
