"""One Line, Every Field, No Secrets — Lesson 9 DEMO.

START SCAFFOLD (tag l09-start): the schema and the redaction
constants are here; the event factory, the validator, the redactor
and main() are yours to write in the lesson. The finished version
lives at tag l09-finish.

Lesson task — write, in this file:
  1. make_events(): the three demo events — one clean, one carrying
     a planted API key, one carrying a planted customer email.
  2. validate_event(event): the list of schema errors for an event
     (missing fields, wrong types); empty means valid.
  3. redact_event(event): a redacted copy of the event plus the
     redaction count — secret keys by exact name, emails by pattern.
  4. main(): emit every event redacted and validated as one JSON
     line each, then print the proof lines: events emitted, schema
     valid count, secrets redacted, and whether either planted
     payload survived into the emitted stream.

Run:  python -m logline.emit
"""
from __future__ import annotations

import json
import re

SCHEMA = {
    "request_id": str, "tenant": str, "model": str,
    "input_tokens": int, "output_tokens": int,
    "total_ms": (int, float), "quality": (int, float),
}
REDACTED = "[REDACTED]"
# Exact key names only: a substring match on "token" would also redact
# input_tokens / output_tokens, which are counts, not credentials.
SECRET_KEYS = ("api_key", "password", "secret", "access_token", "auth_token")
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

# TODO (Lesson 9): make_events, validate_event, redact_event and main
# are written live in the session recording, step by step, from this
# scaffold.
