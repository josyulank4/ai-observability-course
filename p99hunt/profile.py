"""The Mean Is a Lie Your Users Don't Live In — Lesson 29 DEMO.

A latency profiler over 500 requests: p50, p95 and p99 are computed
per pipeline stage (queue, retrieval, time-to-first-token,
generation), never just for the total. The hunt ends with a name:
the stage whose p99 dominates the tail owns the optimisation budget.

Run:  python -m p99hunt.profile
"""
from __future__ import annotations

from obscommon import STAGES, gen_events, percentile

LABELS = {"queue_ms": "queue", "retrieval_ms": "retrieval",
          "ttft_ms": "ttft", "generation_ms": "generation"}


def profile(events: list[dict]) -> dict[str, dict[str, float]]:
    return {stage: {"p50": percentile([e[stage] for e in events], 50),
                    "p95": percentile([e[stage] for e in events], 95),
                    "p99": percentile([e[stage] for e in events], 99)}
            for stage in STAGES}


def dominant_p99(prof: dict[str, dict[str, float]]) -> str:
    return max(STAGES, key=lambda s: prof[s]["p99"])


def main() -> None:
    events = gen_events(n=500, seed=42)
    prof = profile(events)
    print(f"requests profiled: {len(events)}")
    for stage in STAGES:
        p = prof[stage]
        print(f"stage {LABELS[stage]:<10} p50 {p['p50']:>8.1f} ms  "
              f"p95 {p['p95']:>8.1f} ms  p99 {p['p99']:>8.1f} ms")
    total_p99 = percentile([e["total_ms"] for e in events], 99)
    dom = dominant_p99(prof)
    print(f"total p99: {total_p99:.1f} ms")
    print(f"dominant p99 stage: {LABELS[dom]} ({prof[dom]['p99']:.1f} ms "
          f"of the {total_p99:.1f} ms tail)")
    print("p99hunt demo complete")


if __name__ == "__main__":
    main()
