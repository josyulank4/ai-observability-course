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
    print("watchstack demo complete")


if __name__ == "__main__":
    main()
