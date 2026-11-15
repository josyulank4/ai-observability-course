"""The Mean Is a Lie Your Users Don't Live In — Lesson 29 DEMO.

START SCAFFOLD (tag l29-start): the profiler's raw material is
given — the shared telemetry stream, and a means-only summary
someone wrote first, which rates every stage calm and generation
merely "the biggest". In the recorded session you will write, live:
  1. profile       — p50, p95 and p99 per stage, from the same data
  2. dominant_p99  — name the stage that owns the tail
  3. main          — print the table and the verdict

Run:  python -m p99hunt.profile
"""
from __future__ import annotations

from obscommon import STAGES, gen_events, mean, percentile

LABELS = {"queue_ms": "queue", "retrieval_ms": "retrieval",
          "ttft_ms": "ttft", "generation_ms": "generation"}


def stage_means(events: list[dict]) -> dict[str, float]:
    """The first attempt: one mean per stage. (Kept for contrast —
    the hunt replaces it; a mean cannot see a tail.)"""
    return {stage: mean([e[stage] for e in events]) for stage in STAGES}


# TODO (written live in the session): profile, dominant_p99 and
# main — the percentile hunt the lesson runs on the stream above.
