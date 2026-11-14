"""Every Token Has an Owner — Lesson 25 DEMO.

Per-request token cost attribution over the shared telemetry stream:
spend is totalled overall, split by tenant, feature and prompt
version, and the top spender is named. A planted retry storm — forty
duplicate requests from one tenant re-asking the same question — is
isolated and priced separately, because waste you cannot attribute
is waste you cannot stop.

Run:  python -m tokenledger.ledger
"""
from __future__ import annotations

from obscommon import cost_usd, gen_events

RETRY_COUNT = 40


def retry_storm() -> list[dict]:
    """Forty duplicate retries of one acme chat request (the waste)."""
    template = gen_events(n=1, seed=7)[0]
    storm = []
    for i in range(RETRY_COUNT):
        ev = dict(template)
        ev.update({"request_id": f"retry-{i:03d}", "tenant": "acme",
                   "feature": "chat", "prompt_version": "v3",
                   "is_retry": True})
        storm.append(ev)
    return storm


def attribute(events: list[dict], key: str) -> dict[str, float]:
    totals: dict[str, float] = {}
    for e in events:
        totals[e[key]] = totals.get(e[key], 0.0) + cost_usd(e)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def ledger(events: list[dict]) -> dict:
    return {
        "total": sum(cost_usd(e) for e in events),
        "by_tenant": attribute(events, "tenant"),
        "by_feature": attribute(events, "feature"),
        "by_prompt": attribute(events, "prompt_version"),
    }


def main() -> None:
    base = gen_events(n=200, seed=42)
    storm = retry_storm()
    waste = sum(cost_usd(e) for e in storm)
    report = ledger(base + storm)
    print(f"requests: {len(base) + len(storm)} (base {len(base)} + retries {len(storm)})")
    print(f"total token cost: ${report['total']:.4f}")
    for name, dollars in report["by_tenant"].items():
        print(f"tenant {name}: ${dollars:.4f}")
    for name, dollars in report["by_feature"].items():
        print(f"feature {name}: ${dollars:.4f}")
    top = next(iter(report["by_tenant"]))
    print(f"top spender: {top} (${report['by_tenant'][top]:.4f})")
    print(f"retry storm waste: ${waste:.4f} across {len(storm)} duplicate requests")
    print("tokenledger demo complete")


if __name__ == "__main__":
    main()
