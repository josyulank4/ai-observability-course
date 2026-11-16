"""Four Agents, One Bad Answer — Find the First — Lesson 45 DEMO.

A multi-agent pipeline (router -> researcher -> drafter -> reviewer)
produced one failed answer. Every agent's output carries a quality
check, and the trace graph is walked in execution order: blame lands
on the FIRST agent whose output failed its check — the researcher,
who invented a refund window. Downstream agents inherited the error;
punishing them would fix nothing.

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


def first_failure() -> dict:
    for name, dep, check, score, note in AGENTS:
        if score < QUALITY_FLOOR:
            return {"agent": name, "check": check, "score": score,
                    "note": note, "depends_on": dep}
    return {}


def downstream_of(agent: str) -> list[str]:
    seen, frontier = [], [agent]
    graph = {a: dep for a, dep, *_ in AGENTS}
    changed = True
    while changed:
        changed = False
        for name, dep in graph.items():
            if dep in frontier and name not in seen and name != agent:
                seen.append(name)
                frontier.append(name)
                changed = True
    return seen


def main() -> None:
    for name, dep, check, score, note in AGENTS:
        state = "pass" if score >= QUALITY_FLOOR else "FAIL"
        print(f"agent {name:<10} depends_on={dep or '-':<10} "
              f"check '{check}': {score:.2f} {state} — {note}")
    culprit = first_failure()
    print(f"first failing agent: {culprit['agent']} "
          f"(score {culprit['score']:.2f} on '{culprit['check']}')")
    print(f"root cause: {culprit['note']}")
    inheritors = downstream_of(culprit["agent"])
    print(f"downstream agents that inherited the error: {', '.join(inheritors)}")
    print(f"blame: {culprit['agent']} — fix grounding there, not the whole chain")
    print("culprit demo complete")


if __name__ == "__main__":
    main()
