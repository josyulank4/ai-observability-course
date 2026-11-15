"""Models Rot Quietly — Watch for the Drift — Lesson 33 DEMO.

A baseline window is compared against the current window on the two
signals users feel: mean answer quality and hallucination rate. Each
signal carries a threshold; crossing either one raises drift. Nothing
here pages on vibes — the deltas are printed and the thresholds are
named, so the detection can be argued with.

Run:  python -m decayradar.drift
"""
from __future__ import annotations

from obscommon import gen_events, hallucination_rate, mean

QUALITY_DROP_THRESHOLD = 0.05
HALLUC_RISE_THRESHOLD = 0.05


def window_stats(events: list[dict]) -> dict:
    return {"mean_quality": mean([e["quality"] for e in events]),
            "halluc_rate": hallucination_rate(events)}


def compare(baseline: list[dict], current: list[dict]) -> dict:
    b, c = window_stats(baseline), window_stats(current)
    drop = b["mean_quality"] - c["mean_quality"]
    rise = c["halluc_rate"] - b["halluc_rate"]
    return {"baseline": b, "current": c, "quality_drop": drop,
            "halluc_rise": rise,
            "quality_drift": drop > QUALITY_DROP_THRESHOLD,
            "halluc_drift": rise > HALLUC_RISE_THRESHOLD}


def main() -> None:
    baseline = gen_events(n=200, seed=42)
    current = gen_events(n=200, seed=42, quality_shift=-0.18, halluc_rate=0.16)
    r = compare(baseline, current)
    print(f"baseline window: mean quality {r['baseline']['mean_quality']:.3f}, "
          f"hallucination rate {r['baseline']['halluc_rate']:.3f}")
    print(f"current window:  mean quality {r['current']['mean_quality']:.3f}, "
          f"hallucination rate {r['current']['halluc_rate']:.3f}")
    print(f"quality drop: {r['quality_drop']:.3f} (threshold {QUALITY_DROP_THRESHOLD}) "
          f"-> drift: {r['quality_drift']}")
    print(f"hallucination rise: {r['halluc_rise']:.3f} (threshold {HALLUC_RISE_THRESHOLD}) "
          f"-> drift: {r['halluc_drift']}")
    detected = r["quality_drift"] or r["halluc_drift"]
    print(f"drift detected: {detected}")
    print("decayradar demo complete")


if __name__ == "__main__":
    main()
