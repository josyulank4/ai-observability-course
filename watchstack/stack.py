"""The Capstone Build — Lessons 50–51 DEMO. SCAFFOLD (l50-start).

The report shell exists and it already knows the answer: it prints
the header and a SHIP verdict it never computed. No check runs, no
request is observed, and run_checks does not exist — the verdict is
asserted, never earned. The lesson replaces the assertion with the
assembled stack: every check from the course re-run over the support
service, the warnings named first, and the verdict computed from
the checks, never asserted.

Run:  python -m watchstack.stack
"""
from __future__ import annotations


def main() -> None:
    print("== support-chat observability report ==")
    print("verdict: SHIP")
    print("watchstack demo complete")


if __name__ == "__main__":
    main()
