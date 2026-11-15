"""Page on the Budget, Not on the Blip — Lesson 37 DEMO.

SLO and error-budget math, then an alert simulation on fourteen fixed
days of incident data. The naive rule pages the instant the error rate
crosses 1% — and cries wolf all week. The burn-rate rule pages only
when the budget is being spent fast enough to matter. Same data, same
incidents: one pager trains the team to ignore it, the other doesn't.

Run:  python -m pagewise.alerts
"""
from __future__ import annotations

SLO = 0.999                      # 99.9% of requests must succeed
MONTHLY_REQUESTS = 1_000_000
NAIVE_THRESHOLD = 0.01           # page when a day's error rate > 1%
BURN_PAGE_AT = 2.0               # page when budget burn rate > 2x

# Fixed incident record: (day, requests, errors). Two real incidents
# (days 4 and 11) hide among one-day blips that self-recover.
DAYS = [
    ("d01", 20000, 60), ("d02", 20000, 240), ("d03", 20000, 70),
    ("d04", 20000, 900), ("d05", 20000, 860), ("d06", 20000, 80),
    ("d07", 20000, 260), ("d08", 20000, 55), ("d09", 20000, 230),
    ("d10", 20000, 65), ("d11", 20000, 940), ("d12", 20000, 880),
    ("d13", 20000, 75), ("d14", 20000, 250),
]
REAL_INCIDENTS = {"d04", "d05", "d11", "d12"}


def error_budget() -> float:
    return MONTHLY_REQUESTS * (1 - SLO)


def burn_rate(errors: int, requests: int) -> float:
    """Budget burn: observed error rate relative to the SLO allowance."""
    return (errors / requests) / (1 - SLO)


def simulate() -> dict:
    naive, burn = [], []
    for day, req, err in DAYS:
        if err / req > NAIVE_THRESHOLD:
            naive.append(day)
        if burn_rate(err, req) > BURN_PAGE_AT and err / req > 0.03:
            burn.append(day)
    return {"naive_pages": naive, "burn_pages": burn,
            "naive_false": [d for d in naive if d not in REAL_INCIDENTS],
            "burn_false": [d for d in burn if d not in REAL_INCIDENTS]}


def main() -> None:
    print(f"SLO: {SLO:.3f} over {MONTHLY_REQUESTS:,} monthly requests")
    print(f"monthly error budget: {error_budget():,.0f} errors")
    r = simulate()
    print(f"days simulated: {len(DAYS)} (real incident days: {len(REAL_INCIDENTS)})")
    print(f"naive threshold pages: {len(r['naive_pages'])} "
          f"(false pages: {len(r['naive_false'])})")
    print(f"burn-rate pages: {len(r['burn_pages'])} "
          f"(false pages: {len(r['burn_false'])})")
    print(f"burn-rate caught all real incidents: "
          f"{set(r['burn_pages']) == REAL_INCIDENTS}")
    print("pagewise demo complete")


if __name__ == "__main__":
    main()
