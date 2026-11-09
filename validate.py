"""End-to-end validation for the Course 9 code repository.
Runs every lesson demo as a subprocess (exactly how a student runs them)
and checks expected output markers. Run from the repo root: python validate.py
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent
FAILURES = []
COUNT = [0]
def check(name, condition, detail=""):
    COUNT[0] += 1
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition: FAILURES.append(name)
def expect(module, markers):
    proc = subprocess.run([sys.executable, "-m", module], cwd=REPO_ROOT, capture_output=True, text=True, timeout=300)
    check(f"{module}: runs end-to-end (exit 0)", proc.returncode == 0, proc.stderr.strip()[-300:])
    for m in markers: check(f"{module}: output contains {m!r}", m in proc.stdout)
def main():
    print("== module demos (subprocess) ==")
    expect("blindspot.baseline", ["mean quality 0.850", "mean quality 0.530", "mean quality moved -0.320", "hallucinations 0.025 -> 0.195", "blindspot demo complete"])
    expect("logline.emit", ["events emitted: 3", "schema valid: 3/3", "secrets redacted: 2", "planted secret in emitted logs: False", "planted email in emitted logs: False", "logline demo complete"])
    expect("traceweave.trace", ["total time: 2140.0 ms", "critical path: agent-request -> llm-compose", "critical path time: 2120.0 ms", "slowest span: llm-plan (640.0 ms)", "failed span: tool:billing_lookup (status error)", "traceweave demo complete"])
    expect("promptwatch.registry", ["eval cases: 6", "v3 mean quality: 0.890", "v4 mean quality: 0.720", "quality drop: 0.170 (gate: 0.05)", "v4 verdict: REGRESSION", "promptwatch demo complete"])
    expect("judgeaudit.audit", ["cases: 12", "judge-human agreement: 0.750", "mean judge score 0.823", "bias detected: True", "judgeaudit demo complete"])
    expect("tokenledger.ledger", ["requests: 240 (base 200 + retries 40)", "total token cost: $0.4083", "top spender: globex ($0.1524)", "retry storm waste: $0.0091 across 40 duplicate requests", "tokenledger demo complete"])
    expect("p99hunt.profile", ["requests profiled: 500", "total p99: 2081.7 ms", "dominant p99 stage: generation (1786.0 ms of the 2081.7 ms tail)", "p99hunt demo complete"])
    expect("decayradar.drift", ["quality drop: 0.180 (threshold 0.05) -> drift: True", "hallucination rise: 0.110 (threshold 0.05) -> drift: True", "drift detected: True", "decayradar demo complete"])
    expect("pagewise.alerts", ["monthly error budget: 1,000 errors", "naive threshold pages: 8 (false pages: 4)", "burn-rate pages: 4 (false pages: 0)", "burn-rate caught all real incidents: True", "pagewise demo complete"])
    expect("culprit.blame", ["first failing agent: researcher (score 0.21", "root cause: cited a 90-day refund window; policy says 30 days", "downstream agents that inherited the error: drafter, reviewer", "blame: researcher", "culprit demo complete"])
    expect("watchstack.stack", ["requests observed: 200", "mean quality: 0.850", "verdict: SHIP", "watchstack demo complete"])
    print()
    print("== direct assertions ==")
    from obscommon import cost_usd, gen_events, percentile
    check("telemetry dataset is deterministic across calls", gen_events(n=20, seed=42) == gen_events(n=20, seed=42))
    check("percentile of 1..100 at p99 is 99.01", abs(percentile(list(range(1, 101)), 99) - 99.01) < 1e-9)
    check("event cost is positive for a pro-model event", cost_usd(gen_events(n=1, seed=7)[0]) > 0)
    from blindspot.baseline import snapshot
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        b = snapshot("b", gen_events(n=200, seed=42))
        a = snapshot("a", gen_events(n=200, seed=42, quality_shift=-0.32, halluc_rate=0.22))
    check("silent change leaves error rate untouched while quality collapses", b["error_rate"] == a["error_rate"] and a["mean_quality"] < b["mean_quality"] - 0.25)
    from logline.emit import make_events, redact_event, validate_event
    clean, hits = redact_event(make_events()[1])
    check("redaction strips the planted api_key and validates clean", clean["api_key"] == "[REDACTED]" and hits == 1 and not validate_event(clean))
    from traceweave.trace import build_trace, failed_spans, slowest_span, total_ms
    spans = build_trace()
    check("trace total is 2140 ms with billing_lookup the failed span", total_ms(spans) == 2140.0 and failed_spans(spans)[0]["name"] == "tool:billing_lookup")
    check("slowest span is llm-plan", slowest_span(spans)["name"] == "llm-plan")
    from promptwatch.registry import compare
    r = compare()
    check("prompt v4 is a measured regression (drop 0.170)", abs((r["v3_quality"] - r["v4_quality"]) - 0.17) < 1e-9)
    from judgeaudit.audit import audit
    ja = audit()
    check("judge agreement is 0.750 with verbosity bias present", abs(ja["agreement"] - 0.75) < 1e-9 and ja["verbose_wrong_mean"] > ja["concise_right_mean"])
    from tokenledger.ledger import ledger, retry_storm
    led = ledger(gen_events(n=200, seed=42) + retry_storm())
    check("globex is the top-spending tenant", next(iter(led["by_tenant"])) == "globex")
    from p99hunt.profile import dominant_p99, profile
    check("generation dominates the p99 tail", dominant_p99(profile(gen_events(n=500, seed=42))) == "generation_ms")
    from decayradar.drift import compare as drift_compare
    dc = drift_compare(gen_events(n=200, seed=42), gen_events(n=200, seed=42, quality_shift=-0.18, halluc_rate=0.16))
    check("drift detector fires on both signals", dc["quality_drift"] and dc["halluc_drift"])
    from pagewise.alerts import error_budget, simulate
    sim = simulate()
    check("error budget is 1,000 and burn-rate paging has zero false pages", abs(error_budget() - 1000.0) < 1e-6 and len(sim["burn_false"]) == 0 and len(sim["naive_pages"]) == 8)
    from culprit.blame import downstream_of, first_failure
    check("first failing agent is the researcher", first_failure()["agent"] == "researcher" and downstream_of("researcher") == ["drafter", "reviewer"])
    print()
    if FAILURES:
        print(f"OVERALL: FAIL ({len(FAILURES)} failures)"); return 1
    print(f"OVERALL: PASS ({COUNT[0]} checks)")
    return 0
if __name__ == "__main__":
    sys.exit(main())
