"""A Prompt Is a Release — Version It Like One — Lesson 17 DEMO.

A prompt registry holding two versions of the support-chat system
prompt. The demo diffs the versions line by line, then compares their
measured quality and cost on a fixed six-case eval set. The new
version is cheaper — and it is a regression: quality falls past the
gate, so the registry flags it instead of shipping it.

Run:  python -m promptwatch.registry
"""
from __future__ import annotations

from obscommon import mean

REGISTRY = {
    "v3": [
        "You are a support assistant for a SaaS product.",
        "Answer only from the retrieved policy documents.",
        "Cite the policy section for every factual claim.",
        "If the documents do not answer, say so and escalate.",
        "Keep answers under 180 words.",
    ],
    "v4": [
        "You are a friendly support assistant.",
        "Answer helpfully from the retrieved policy documents.",
        "Keep answers under 90 words.",
        "Always sound confident, even when unsure.",
    ],
}

# Fixed eval set: (case, v3 quality, v4 quality, v3 cost $, v4 cost $)
EVAL_SET = [
    ("refund-window", 0.92, 0.74, 0.0041, 0.0026),
    ("reset-2fa", 0.90, 0.71, 0.0038, 0.0024),
    ("invoice-copy", 0.88, 0.76, 0.0035, 0.0023),
    ("api-quota", 0.86, 0.68, 0.0044, 0.0028),
    ("damaged-parcel", 0.91, 0.73, 0.0039, 0.0025),
    ("sso-setup", 0.87, 0.70, 0.0040, 0.0026),
]
QUALITY_GATE_DROP = 0.05


def diff_versions(old: list[str], new: list[str]) -> tuple[list[str], list[str]]:
    removed = [line for line in old if line not in new]
    added = [line for line in new if line not in old]
    return removed, added


def compare() -> dict:
    return {
        "v3_quality": mean([c[1] for c in EVAL_SET]),
        "v4_quality": mean([c[2] for c in EVAL_SET]),
        "v3_cost": sum(c[3] for c in EVAL_SET),
        "v4_cost": sum(c[4] for c in EVAL_SET),
    }


def main() -> None:
    removed, added = diff_versions(REGISTRY["v3"], REGISTRY["v4"])
    print("prompt diff v3 -> v4:")
    for line in removed:
        print(f"  - {line}")
    for line in added:
        print(f"  + {line}")
    r = compare()
    drop = r["v3_quality"] - r["v4_quality"]
    print(f"eval cases: {len(EVAL_SET)}")
    print(f"v3 mean quality: {r['v3_quality']:.3f}  total cost: ${r['v3_cost']:.4f}")
    print(f"v4 mean quality: {r['v4_quality']:.3f}  total cost: ${r['v4_cost']:.4f}")
    print(f"quality drop: {drop:.3f} (gate: {QUALITY_GATE_DROP})")
    verdict = "REGRESSION" if drop > QUALITY_GATE_DROP else "OK"
    print(f"v4 verdict: {verdict} — cheaper, but quality fell past the gate; do not promote")
    print("promptwatch demo complete")


if __name__ == "__main__":
    main()
