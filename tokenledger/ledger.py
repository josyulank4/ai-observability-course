"""Every Token Has an Owner — Lesson 25 DEMO.

START SCAFFOLD (tag l25-start): the planted retry storm — forty
duplicate requests from one tenant re-asking the same question — is
given, on the shared telemetry stream. In the recorded session you
will write, live:
  1. attribute — total the spend by any key: tenant, feature,
     prompt version
  2. ledger    — the week's totals, reconciled two ways
  3. main      — name the top spender and price the storm

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


# TODO (written live in the session): attribute, ledger and main —
# the attribution ledger the lesson builds on the stream above.
