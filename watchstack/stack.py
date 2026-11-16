"""The Capstone Build — Lessons 50–51 DEMO.

The whole course in one report: structured-log validation and
redaction (logline), one traced request (traceweave), token cost
attribution (tokenledger), per-stage tail latency (p99hunt), drift
against the baseline window (decayradar) and the SLO error budget
(pagewise) are run over the support-chat service and printed as a
single observability report. The ship verdict is computed from the
checks, never asserted: SHIP only when every gate passes. Warnings
are printed above the verdict, honestly, either way.

Run:  python -m watchstack.stack
"""
from __future__ import annotations

from decayradar.drift import compare as drift_compare
from logline.emit import make_events, redact_event, validate_event
from obscommon import gen_events, mean, percentile
from p99hunt.profile import LABELS, dominant_p99, profile
from pagewise.alerts import error_budget, simulate
from tokenledger.ledger import ledger
from traceweave.trace import build_trace, failed_spans, slowest_span, total_ms

P99_BUDGET_MS = 2600.0


def run_checks() -> tuple[list[str], list[str]]:
    checks, warnings = [], []
    events = gen_events(n=200, seed=42)

    raw_logs = make_events()
    emitted = [redact_event(e)[0] for e in raw_logs]
    valid = sum(1 for e in emitted if not validate_event(e))
    leaked = any("PLANTED-SECRET" in str(e) for e in emitted)
    checks.append(("logs schema-valid and secret-free",
                   valid == len(emitted) and not leaked))

    spans = build_trace()
    checks.append((f"trace captured end-to-end (total {total_ms(spans):.0f} ms, "
                   f"failed spans surfaced, not hidden)",
                   total_ms(spans) > 0))
    if failed_spans(spans):
        warnings.append(f"trace contains {len(failed_spans(spans))} failed span "
                        f"({failed_spans(spans)[0]['name']}) — tracked, non-blocking "
                        f"for read-only answers; slowest span "
                        f"{slowest_span(spans)['name']} over {total_ms(spans):.0f} ms total")

    report = ledger(events)
    checks.append((f"token spend attributed (total ${report['total']:.4f})",
                   report["total"] > 0 and len(report["by_tenant"]) == 3))

    prof = profile(events)
    tail = percentile([e["total_ms"] for e in events], 99)
    checks.append((f"total p99 {tail:.1f} ms within {P99_BUDGET_MS:.0f} ms budget",
                   tail <= P99_BUDGET_MS))
    warnings.append(f"dominant p99 stage is {LABELS[dominant_p99(prof)]} — "
                    f"the optimisation target, inside budget today")

    healthy_current = gen_events(n=200, seed=99)
    drift = drift_compare(events, healthy_current)
    checks.append(("no quality or hallucination drift vs baseline",
                   not drift["quality_drift"] and not drift["halluc_drift"]))

    sim = simulate()
    checks.append((f"error budget {error_budget():,.0f} errors/mo; burn-rate "
                    f"paging false pages {len(sim['burn_false'])}",
                   len(sim["burn_false"]) == 0))
    warnings.append(f"naive threshold paging would have fired "
                    f"{len(sim['naive_false'])} false pages on the same data")
    return checks, warnings


def review() -> tuple[int, int, int]:
    """Walk the manuscript's Appendix A checklist line by line.

    Every item is graded from evidence this run itself produced, or
    it is graded OPEN, with the reason printed. A measured item that
    fails is a blocker and holds the ship. The review verdict is
    computed from the grades, exactly like the report verdict above
    it: obligations may ship, named — a failed measurement may not.
    """
    import json

    events = gen_events(n=200, seed=42)
    logs = [redact_event(e)[0] for e in make_events()]
    logs_clean = (all(not validate_event(e) for e in logs)
                  and not any("PLANTED-SECRET" in str(e) for e in logs))
    spans = build_trace()
    span_names = [s["name"] for s in spans]
    rep = ledger(events)
    tail = percentile([e["total_ms"] for e in events], 99)
    drift = drift_compare(events, gen_events(n=200, seed=99))
    sim = simulate()
    payload = len(json.dumps(events).encode())

    # (section, item, measured, grade, evidence)
    items = [
        ("instrumentation",
         "structured log event: request id, model, prompt version, token counts, latency",
         True,
         all(all(k in e for k in ("request_id", "model", "prompt_version",
                                  "input_tokens", "output_tokens",
                                  "total_ms")) for e in events),
         "carried on all 200 request events"),
        ("instrumentation",
         "correlation ids propagate across every service, agent and tool call",
         True,
         all(e["request_id"] for e in events) and len(spans) == 6
         and all(s["parent"] for s in spans if s["name"] != "agent-request"),
         "one trace, six parent-linked spans; a request id on every event"),
        ("instrumentation",
         "PII redaction runs before telemetry leaves the application boundary",
         True, logs_clean,
         "every emitted log line validated clean; the planted secret absent"),
        ("instrumentation",
         "traces carry spans for planning, tool calls and retries",
         False, False,
         "planning and tool-call spans are measured in the trace; the stack emits no retry span"),
        ("instrumentation",
         "prompt versions are recorded on every request, not just in git",
         True,
         all(e["prompt_version"] for e in events),
         "a prompt version on all 200 events; spend attributes by prompt version"),
        ("quality",
         "an eval harness samples live traffic and scores it on a schedule",
         False, False,
         f"this run scores its 200 requests (mean quality {mean([e['quality'] for e in events]):.3f}); the sampling schedule is an operations commitment no single run can evidence"),
        ("quality",
         "a golden dataset regression runs on every prompt or model change",
         False, False,
         "no golden suite ships with the stack; the drift comparison is a baseline-window check, not a golden regression"),
        ("quality",
         "judge scores are calibrated against human labels quarterly",
         False, False,
         "a quarterly human practice; no code run can evidence it"),
        ("quality",
         "hallucination and faithfulness metrics are tracked, with alerts on drift",
         True,
         not drift["quality_drift"] and not drift["halluc_drift"],
         "drift against the baseline window measured on both signals: none"),
        ("quality",
         "user feedback signals feed the quality dashboard",
         False, False,
         "no feedback signal exists anywhere in the data this stack keeps"),
        ("cost and performance",
         "token usage is attributed to user, team, feature and prompt version",
         True,
         len(rep["by_tenant"]) == 3 and bool(rep["by_feature"])
         and bool(rep["by_prompt"]),
         f"total ${rep['total']:.4f} split by tenant, by feature and by prompt version"),
        ("cost and performance",
         "spend budgets with circuit breakers are enforced per tenant or workload",
         False, False,
         "the stack reports spend per tenant; no breaker trips anywhere in this code"),
        ("cost and performance",
         "cost anomaly alerts fire on retry storms and runaway agents",
         False, False,
         "no storm watch runs in the assembled stack; the instrument exists in the ledger lesson, unassembled"),
        ("cost and performance",
         "TTFT and end-to-end latency percentiles are measured per endpoint",
         True,
         bool(profile(events)) and all("ttft_ms" in e for e in events),
         f"per-stage profile measured; total p99 {tail:.1f} ms; TTFT carried on every event"),
        ("cost and performance",
         "latency budgets exist and are reviewed when p99 degrades",
         True, tail <= P99_BUDGET_MS,
         f"a {P99_BUDGET_MS:.0f} ms budget named in the source; the check compares on every run"),
        ("alerting and response",
         "SLOs are defined for quality, latency and cost, not just uptime",
         False, False,
         f"an error budget of {error_budget():,.0f} errors and a latency budget are defined; no cost SLO threshold ships"),
        ("alerting and response",
         "paging is reserved for burn-rate breaches",
         True,
         len(sim["burn_false"]) == 0 and len(sim["naive_false"]) == 4,
         "burn-rate paging fires 4 pages, none false; the naive rule fires 4 false pages on the same data"),
        ("alerting and response",
         "an incident runbook exists and the on-call rotation has practiced it",
         False, False,
         "a team practice; Lesson 49's contract names the duties, but practice cannot be evidenced by a run"),
        ("alerting and response",
         "postmortems are blameless and produce systemic fixes, not just prompt tweaks",
         False, False,
         "a team practice, outside anything this code can show"),
        ("debugging readiness",
         "a debug harness can replay any failing query with its retrieved chunks and scores",
         False, False,
         "no replay harness ships with the stack"),
        ("debugging readiness",
         "conversation replay works from stored traces",
         False, False,
         "traces are assembled in memory for the report; nothing is stored to replay from"),
        ("debugging readiness",
         "dashboards exist for volume, quality, cost, latency and eval trends",
         False, False,
         "the report prints volume, quality, cost and latency as text; no dashboard ships with the stack"),
    ]
    print("== production observability checklist (Appendix A) ==")
    evidenced = opened = blockers = 0
    section = None
    for sec, item, measured, grade, evidence in items:
        if sec != section:
            section = sec
            print(f"--- {sec} ---")
        if measured and grade:
            label = "EVIDENCED"
            evidenced += 1
        elif measured:
            label = "FAIL"
            blockers += 1
        else:
            label = "OPEN"
            opened += 1
        print(f"review [{label}] {item}: {evidence}")
    print(f"telemetry bill: watching 200 requests produced {payload:,} bytes "
          f"of request telemetry ({payload / 200:.0f} bytes a request)")
    print(f"telemetry bill: the watcher read two windows of 200 requests to "
          f"judge one; the observed token bill was ${rep['total']:.4f}")
    print(f"checklist: {evidenced} of {len(items)} items evidenced by the "
          f"running stack; {opened} open obligations; {blockers} blockers")
    return evidenced, opened, blockers


def main() -> None:
    events = gen_events(n=200, seed=42)
    print("== support-chat observability report ==")
    print(f"requests observed: {len(events)}")
    print(f"mean quality: {mean([e['quality'] for e in events]):.3f}")
    checks, warnings = run_checks()
    for name, ok in checks:
        print(f"check [{'PASS' if ok else 'FAIL'}] {name}")
    for w in warnings:
        print(f"warning: {w}")
    verdict = "SHIP" if all(ok for _, ok in checks) else "HOLD"
    print(f"verdict: {verdict}")
    _, _, blockers = review()
    if blockers == 0:
        print("review verdict: SHIP — the stack ships; the obligations ship with it, named")
    else:
        print("review verdict: HOLD — measured items failed; the stack does not ship")
    print("watchstack demo complete")


if __name__ == "__main__":
    main()
