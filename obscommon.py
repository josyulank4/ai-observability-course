"""Deterministic, stdlib-only helpers shared by every Course 9 demo package.

One synthetic telemetry dataset for a support-chat AI service, a small
token price table, and the statistics helpers every package grades
itself with. No randomness without a fixed seed, no network, no
third-party packages: every number in this course reproduces exactly,
on every machine, on every run.
"""
from __future__ import annotations

import random

# Token prices in USD per 1,000 tokens (illustrative planning figures;
# the attribution arithmetic, not the vendor, is the content).
PRICE_PER_1K = {
    "chat-small": {"input": 0.0002, "output": 0.0006},
    "chat-pro": {"input": 0.0030, "output": 0.0120},
}

TENANTS = ("acme", "globex", "initech")
FEATURES = ("chat", "summarize", "ticket-triage")
STAGES = ("queue_ms", "retrieval_ms", "ttft_ms", "generation_ms")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(values: list[float], p: float) -> float:
    """Linear-interpolation percentile (the numpy default method)."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = (p / 100.0) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac


def cost_usd(event: dict) -> float:
    """Dollar cost of one request event from the price table."""
    price = PRICE_PER_1K[event["model"]]
    return (event["input_tokens"] * price["input"]
            + event["output_tokens"] * price["output"]) / 1000.0


def gen_events(n: int = 200, seed: int = 42, quality_shift: float = 0.0,
               halluc_rate: float = 0.04) -> list[dict]:
    """Fixed-seed synthetic request events for the support-chat service.

    Same arguments, same events, forever. `quality_shift` lowers every
    quality score (a silent model change); `halluc_rate` is the planted
    hallucination probability. Latency stages are deliberately uneven:
    generation dominates the tail, which Lesson 29 hunts down.
    """
    rng = random.Random(seed)
    events = []
    for i in range(n):
        tenant = TENANTS[i % len(TENANTS)]
        feature = FEATURES[rng.randrange(len(FEATURES))]
        model = "chat-pro" if feature == "ticket-triage" else "chat-small"
        queue = round(rng.uniform(2, 30), 1)
        retrieval = round(rng.uniform(15, 120), 1)
        ttft = round(rng.uniform(60, 260), 1)
        generation = round(rng.uniform(400, 1800), 1)
        quality = round(min(0.99, max(0.05,
                        rng.uniform(0.72, 0.98) + quality_shift)), 3)
        events.append({
            "request_id": f"req-{i:04d}",
            "tenant": tenant,
            "feature": feature,
            "prompt_version": "v3",
            "model": model,
            "input_tokens": rng.randrange(120, 900),
            "output_tokens": rng.randrange(80, 620),
            "queue_ms": queue,
            "retrieval_ms": retrieval,
            "ttft_ms": ttft,
            "generation_ms": generation,
            "total_ms": round(queue + retrieval + ttft + generation, 1),
            "quality": quality,
            "hallucinated": rng.random() < halluc_rate,
            "tool_calls": rng.randrange(0, 4),
            "status": 500 if rng.random() < 0.01 else 200,
        })
    return events


def error_rate(events: list[dict]) -> float:
    if not events:
        return 0.0
    return sum(1 for e in events if e["status"] >= 500) / len(events)


def hallucination_rate(events: list[dict]) -> float:
    if not events:
        return 0.0
    return sum(1 for e in events if e["hallucinated"]) / len(events)
