"""Grade the Grader Before You Trust It — Lesson 21 DEMO.

START SCAFFOLD (tag l21-start): the fixed case set — twelve answers
humans have already labelled, with the judge's scores and word
counts — and the pass rule are given. In the recorded session you
will write, live:
  1. audit — agreement with the humans, and the verbosity probe:
     verbose wrong answers vs concise correct ones
  2. main  — print every case, the agreement, and the bias verdict

Run:  python -m judgeaudit.audit
"""
from __future__ import annotations

from obscommon import mean

# (answer_id, human_pass, judge_score 0..1, word_count)
CASES = [
    ("a01", True, 0.91, 142),
    ("a02", True, 0.88, 118),
    ("a03", True, 0.62, 41),    # concise + correct: judge underrates it
    ("a04", True, 0.58, 36),    # concise + correct: judge underrates it
    ("a05", True, 0.90, 129),
    ("a06", True, 0.84, 105),
    ("a07", False, 0.86, 388),  # verbose + wrong: judge overrates it
    ("a08", False, 0.82, 342),  # verbose + wrong: judge overrates it
    ("a09", False, 0.79, 301),  # verbose + wrong: judge overrates it
    ("a10", False, 0.31, 88),
    ("a11", False, 0.27, 64),
    ("a12", False, 0.22, 52),
]
PASS_AT = 0.50
VERBOSE_WORDS = 250


def judge_pass(score: float) -> bool:
    return score >= PASS_AT


# TODO (written live in the session): audit and main — the audit
# harness the lesson builds on the case set above.
