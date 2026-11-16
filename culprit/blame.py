"""Four Agents, One Bad Answer — Find the First — Lesson 45 DEMO (SCAFFOLD).

Starting point for the hands-on session: a multi-agent pipeline
(router -> researcher -> drafter -> reviewer) produced one failed
answer, and every agent's output carries a quality check. The only
blame rule here is the one most teams start with — blame the agent
that touched the answer last. Run it and meet the accused. The
execution-order localiser does not exist yet; that is what the
session builds.

Run:  python -m culprit.blame
"""
from __future__ import annotations

QUALITY_FLOOR = 0.60

# (agent, depends_on, check, score, note) in execution order.
AGENTS = [
    ("router", None, "intent classified", 0.94, "intent: refund question"),
    ("researcher", "router", "facts grounded in policy docs", 0.21,
     "cited a 90-day refund window; policy says 30 days"),
    ("drafter", "researcher", "draft follows supplied facts", 0.88,
     "draft faithfully used the researcher's facts"),
    ("reviewer", "drafter", "final answer checked", 0.42,
     "approved the draft without re-checking the window"),
]


def trace_graph() -> dict[str, list[str]]:
    return {a: ([dep] if dep else []) for a, dep, *_ in AGENTS}


def blame_last() -> dict:
    name, dep, check, score, note = AGENTS[-1]
    return {"agent": name, "check": check, "score": score,
            "note": note, "depends_on": dep}


def main() -> None:
    for name, dep, check, score, note in AGENTS:
        state = "pass" if score >= QUALITY_FLOOR else "FAIL"
        print(f"agent {name:<10} depends_on={dep or '-':<10} "
              f"check '{check}': {score:.2f} {state} — {note}")
    accused = blame_last()
    print(f"naive blame: {accused['agent']} — last to touch the answer")


if __name__ == "__main__":
    main()
