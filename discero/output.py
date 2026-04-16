"""Serialize pipeline state to course.json and validate on both sides."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from . import GENERATED_BY, SCHEMA_VERSION
from .schemas import CourseBody, CoursePayload
from .state import PipelineState


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_payload(state: PipelineState) -> CoursePayload:
    outline = state["outline"]
    chapters = state.get("chapters", [])
    if not chapters:
        raise RuntimeError("pipeline produced no chapters")

    # Use outline estimated hours for `course.duration` floor is just `duration_weeks`.
    body = CourseBody(
        subject=state["subject"],
        duration=state["duration_weeks"],
        outline=outline,
        chapters=chapters,
    )

    return CoursePayload(
        schemaVersion=SCHEMA_VERSION,  # type: ignore[arg-type]
        generatedBy=GENERATED_BY,
        generatedAt=_iso_now(),
        course=body,
    )


def write_payload(payload: CoursePayload, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            payload.model_dump(mode="json", exclude_none=False),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def validate_file(path: Path) -> CoursePayload:
    """Load and validate a course.json against the Pydantic schema.

    Raises ValidationError on schema mismatch; the caller prints the
    field path. Raises JSONDecodeError on invalid JSON.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CoursePayload.model_validate(raw)


def format_validation_error(e: ValidationError) -> str:
    lines = ["Validation failed:"]
    for err in e.errors():
        loc = ".".join(str(x) for x in err["loc"]) or "(root)"
        lines.append(f"  - {loc}: {err['msg']}")
    return "\n".join(lines)
