"""The Dashboard Was Green While Answers Died — Lesson 5 DEMO.

The observability gap, in numbers: the same request stream is measured
twice — before a silent model change, and after it. The latency and
error signals an infrastructure dashboard watches barely move, while
answer quality collapses and hallucinations multiply. If you only
watch the machine, you never see the product break.

Run:  python -m blindspot.baseline
"""
from __future__ import annotations

from obscommon import error_rate, gen_events, hallucination_rate, mean, percentile


def snapshot(label: str, events: list[dict]) -> dict:
    stats = {
        "label": label,
        "error_rate": error_rate(events),
        "p95_ms": percentile([e["total_ms"] for e in events], 95),
        "mean_quality": mean([e["quality"] for e in events]),
        "halluc_rate": hallucination_rate(events),
    }
    print(f"{label}: error rate {stats['error_rate']:.3f}, "
          f"p95 latency {stats['p95_ms']:.1f} ms, "
          f"mean quality {stats['mean_quality']:.3f}, "
          f"hallucination rate {stats['halluc_rate']:.3f}")
    return stats


def main() -> None:
    before = gen_events(n=200, seed=42)
    after = gen_events(n=200, seed=42, quality_shift=-0.32, halluc_rate=0.22)
    b = snapshot("before silent model change", before)
    a = snapshot("after  silent model change", after)
    print(f"infra verdict: error rate moved {a['error_rate'] - b['error_rate']:+.3f}, "
          f"p95 moved {a['p95_ms'] - b['p95_ms']:+.1f} ms — dashboard stays green")
    print(f"quality verdict: mean quality moved {a['mean_quality'] - b['mean_quality']:+.3f}, "
          f"hallucinations {b['halluc_rate']:.3f} -> {a['halluc_rate']:.3f} — users see the break")
    print("blindspot demo complete")


if __name__ == "__main__":
    main()
