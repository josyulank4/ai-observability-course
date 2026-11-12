"""The Dashboard Was Green While Answers Died — Lesson 5 DEMO.

START SCAFFOLD (tag l05-start): the plumbing is here; the snapshot
function and main() are yours to write in the lesson. The finished
version lives at tag l05-finish.

Lesson task — write, in this file:
  1. snapshot(label, events): compute error rate, p95 latency, mean
     quality and hallucination rate for one event stream, print the
     snapshot line, and return the stats.
  2. main(): generate the week's traffic twice from the same seed —
     before the silent model change and after it (quality shifted
     down, hallucination rate planted higher) — snapshot both, and
     print the infra verdict and the quality verdict.

Run:  python -m blindspot.baseline
"""
from __future__ import annotations

from obscommon import error_rate, gen_events, hallucination_rate, mean, percentile

# TODO (Lesson 5): snapshot and main are written live in the session
# recording, step by step, from this scaffold.
