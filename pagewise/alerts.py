"""Page on the Budget, Not on the Blip — Lesson 37 DEMO (SCAFFOLD).

Starting point for the hands-on session: the incident record and the
error-budget math are here, and so is the paging rule most teams
start with — page the instant a day's error rate crosses one percent.
Run it and count the pages. The burn-rate rule does not exist yet;
that is what the session builds.

Run:  python -m pagewise.alerts
"""
from __future__ import annotations

SLO = 0.999                      # 99.9% of requests must succeed
MONTHLY_REQUESTS = 1_000_000
NAIVE_THRESHOLD = 0.01           # page when a day's error rate > 1%

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


def naive_pages() -> list:
    return [day for day, req, err in DAYS if err / req > NAIVE_THRESHOLD]


def main() -> None:
    print(f"SLO: {SLO:.3f} over {MONTHLY_REQUESTS:,} monthly requests")
    print(f"monthly error budget: {error_budget():,.0f} errors")
    pages = naive_pages()
    false_pages = [d for d in pages if d not in REAL_INCIDENTS]
    print(f"days simulated: {len(DAYS)} (real incident days: {len(REAL_INCIDENTS)})")
    print(f"naive threshold pages: {len(pages)} (false pages: {len(false_pages)})")
    print("TODO: the burn-rate rule does not exist yet")


if __name__ == "__main__":
    main()
