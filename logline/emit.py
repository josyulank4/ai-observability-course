"""One Line, Every Field, No Secrets — Lesson 9 DEMO.

Structured JSON log events with a fixed schema. Every event is
validated against the schema before it ships, and a redaction pass
strips planted secrets and PII (an API key, a customer email) so the
proof is in the output: the raw event leaks, the emitted event does
not. Observability that logs credentials is a breach with timestamps.

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


def make_events() -> list[dict]:
    base = [
        {"request_id": "req-0001", "tenant": "acme", "model": "chat-small",
         "input_tokens": 412, "output_tokens": 233, "total_ms": 1180.4,
         "quality": 0.91},
        {"request_id": "req-0002", "tenant": "globex", "model": "chat-pro",
         "input_tokens": 801, "output_tokens": 402, "total_ms": 1975.0,
         "quality": 0.87, "api_key": "sk-live-9f27-PLANTED-SECRET"},
        {"request_id": "req-0003", "tenant": "initech", "model": "chat-small",
         "input_tokens": 260, "output_tokens": 140, "total_ms": 940.2,
         "quality": 0.93, "customer_email": "jane.doe@example.com"},
    ]
    return base


def validate_event(event: dict) -> list[str]:
    errors = []
    for field, types in SCHEMA.items():
        if field not in event:
            errors.append(f"missing field: {field}")
        elif not isinstance(event[field], types):
            errors.append(f"wrong type: {field}")
    return errors


def redact_event(event: dict) -> tuple[dict, int]:
    clean, hits = {}, 0
    for key, value in event.items():
        if key.lower() in SECRET_KEYS:
            clean[key] = REDACTED
            hits += 1
        elif isinstance(value, str) and EMAIL.search(value):
            clean[key] = EMAIL.sub(REDACTED, value)
            hits += 1
        else:
            clean[key] = value
    return clean, hits


def main() -> None:
    events = make_events()
    valid, redactions = 0, 0
    for raw in events:
        clean, hits = redact_event(raw)
        errors = validate_event(clean)
        valid += 0 if errors else 1
        redactions += hits
        print(json.dumps(clean, sort_keys=True))
    blob = json.dumps([redact_event(e)[0] for e in events])
    print(f"events emitted: {len(events)}")
    print(f"schema valid: {valid}/{len(events)}")
    print(f"secrets redacted: {redactions}")
    print(f"planted secret in emitted logs: {'PLANTED-SECRET' in blob}")
    print(f"planted email in emitted logs: {'jane.doe@example.com' in blob}")
    print("logline demo complete")


if __name__ == "__main__":
    main()
