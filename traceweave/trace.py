"""Follow One Request Through the Agent — Lesson 13 DEMO.

One agent request as a span tree: a root span holding retrieval, LLM
and tool spans, each with a start offset and a duration. The demo
computes the wall-clock total, walks the critical path (the chain of
children that actually decides when the request finishes), names the
slowest span, and surfaces the planted failed tool span that a flat
log line would have buried.

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


def total_ms(spans: list[dict]) -> float:
    return max(s["end_ms"] for s in spans) - min(s["start_ms"] for s in spans)


def critical_path(spans: list[dict]) -> list[dict]:
    """Root, then repeatedly the child that finishes last: the chain
    that decides when the request can complete."""
    children: dict[str, list[dict]] = {}
    for s in spans:
        if s["parent"] is not None:
            children.setdefault(s["parent"], []).append(s)
    root = next(s for s in spans if s["parent"] is None)
    path = [root]
    while children.get(path[-1]["name"]):
        path.append(max(children[path[-1]["name"]],
                        key=lambda s: s["end_ms"]))
    return path


def critical_path_ms(spans: list[dict]) -> float:
    path = critical_path(spans)
    return path[-1]["end_ms"] - path[0]["start_ms"]


def slowest_span(spans: list[dict]) -> dict:
    return max((s for s in spans if s["kind"] != "root"),
               key=lambda s: s["dur_ms"])


def failed_spans(spans: list[dict]) -> list[dict]:
    return [s for s in spans if s["status"] == "error"]


def main() -> None:
    spans = build_trace()
    for s in spans:
        print(f"span {s['name']:<22} kind={s['kind']:<9} "
              f"start {s['start_ms']:>7.1f} ms  dur {s['dur_ms']:>6.1f} ms  {s['status']}")
    path = critical_path(spans)
    print(f"total time: {total_ms(spans):.1f} ms")
    print(f"critical path: {' -> '.join(s['name'] for s in path)}")
    print(f"critical path time: {critical_path_ms(spans):.1f} ms "
          f"(request cannot finish before the finishing chain ends)")
    slow = slowest_span(spans)
    print(f"slowest span: {slow['name']} ({slow['dur_ms']:.1f} ms)")
    for f in failed_spans(spans):
        print(f"failed span: {f['name']} (status {f['status']})")
    print("traceweave demo complete")


if __name__ == "__main__":
    main()
