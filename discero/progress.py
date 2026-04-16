"""Minimal stderr progress reporter.

Stages are numbered 1..N so users can see where the pipeline is. Chapter
loop substeps use a fractional `n/N` suffix. Anything printed here goes
to stderr so the final JSON can still be piped to stdout if needed.
"""
from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from typing import Iterator


TOTAL_STAGES = 5


def _stamp() -> str:
    return time.strftime("%H:%M:%S")


def log(stage: int, label: str, detail: str = "") -> None:
    tail = f" — {detail}" if detail else ""
    print(f"[{_stamp()}] [{stage}/{TOTAL_STAGES}] {label}{tail}", file=sys.stderr, flush=True)


def info(msg: str) -> None:
    print(f"[{_stamp()}] {msg}", file=sys.stderr, flush=True)


def warn(msg: str) -> None:
    print(f"[{_stamp()}] WARN: {msg}", file=sys.stderr, flush=True)


def error(msg: str) -> None:
    print(f"[{_stamp()}] ERROR: {msg}", file=sys.stderr, flush=True)


@contextmanager
def stage(stage_num: int, label: str) -> Iterator[None]:
    log(stage_num, f"{label}…")
    start = time.time()
    yield
    log(stage_num, f"{label} done", f"{time.time() - start:.1f}s")
