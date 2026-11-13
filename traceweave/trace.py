"""Follow One Request Through the Agent — Lesson 13 DEMO.

START SCAFFOLD (tag l13-start): the SPANS table and the dict builder
are given. In the recorded session you will write, live:
  1. total_ms        — wall-clock span of the whole request
  2. critical_path   — root, then repeatedly the child that finishes last
  3. critical_path_ms
  4. slowest_span    — longest non-root span by duration
  5. failed_spans    — every span whose status is error

Run:  python -m traceweave.trace
"""
from __future__ import annotations

# (name, kind, parent, start_ms, dur_ms, status)
SPANS = [
    ("agent-request", "root", None, 0.0, 2140.0, "ok"),
    ("retrieve-docs", "retrieval", "agent-request", 20.0, 180.0, "ok"),
    ("llm-plan", "llm", "agent-request", 210.0, 640.0, "ok"),
    ("tool:account_lookup", "tool", "agent-request", 860.0, 240.0, "ok"),
    ("tool:billing_lookup", "tool", "agent-request", 1110.0, 390.0, "error"),
    ("llm-compose", "llm", "agent-request", 1510.0, 610.0, "ok"),
]


def build_trace() -> list[dict]:
    return [{"name": n, "kind": k, "parent": p, "start_ms": s,
             "dur_ms": d, "end_ms": s + d, "status": st}
            for n, k, p, s, d, st in SPANS]


# TODO (written live in the session): total_ms, critical_path,
# critical_path_ms, slowest_span, failed_spans and main — the analysis
# the lesson builds on top of the span table above.
