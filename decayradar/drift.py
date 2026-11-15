"""Models Rot Quietly — Watch for the Drift — Lesson 33 DEMO.

START SCAFFOLD (tag l33-start): the radar's measuring instrument
is given — window_stats reads a window's mean quality and
hallucination rate — and the two thresholds are named, drawn before
any data is read. In the recorded session you will write, live:
  1. compare — baseline vs current, delta by delta, threshold by
     threshold, each signal firing or silent on its own evidence
  2. main    — run the radar on the planted decay, print the verdict

Run:  python -m decayradar.drift
"""
from __future__ import annotations

from obscommon import gen_events, hallucination_rate, mean

QUALITY_DROP_THRESHOLD = 0.05
HALLUC_RISE_THRESHOLD = 0.05


def window_stats(events: list[dict]) -> dict:
    return {"mean_quality": mean([e["quality"] for e in events]),
            "halluc_rate": hallucination_rate(events)}


# TODO (written live in the session): compare and main — the radar
# the lesson builds on the instrument above.
