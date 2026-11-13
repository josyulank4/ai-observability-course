"""A Prompt Is a Release — Version It Like One — Lesson 17 DEMO.

START SCAFFOLD (tag l17-start): the registry (two prompt versions),
the fixed eval set and the quality gate are given. In the recorded
session you will write, live:
  1. diff_versions — lines removed / added between two versions
  2. compare       — mean quality and total cost per version
  3. main          — print the diff, the scores and the gate verdict

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


# TODO (written live in the session): diff_versions, compare and
# main — the release gate the lesson builds on the registry above.
