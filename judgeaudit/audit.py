"""Grade the Grader Before You Trust It — Lesson 21 DEMO.

An LLM judge scores twelve fixed answers that humans have already
labelled. The audit measures agreement honestly — and finds the
planted bias: the judge rewards length, so verbose wrong answers
outscore concise right ones. A judge you have not audited is just a
second model hallucinating with confidence.

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


def audit() -> dict:
    agree = sum(1 for _, human, score, _ in CASES if judge_pass(score) == human)
    verbose_wrong = [s for _, h, s, w in CASES if not h and w >= VERBOSE_WORDS]
    concise_right = [s for _, h, s, w in CASES if h and w < 100]
    return {
        "agreement": agree / len(CASES),
        "verbose_wrong_mean": mean(verbose_wrong),
        "concise_right_mean": mean(concise_right),
        "verbose_wrong_n": len(verbose_wrong),
        "concise_right_n": len(concise_right),
    }


def main() -> None:
    for cid, human, score, words in CASES:
        mark = "AGREE" if judge_pass(score) == human else "DISAGREE"
        print(f"{cid}: human={'pass' if human else 'fail'} "
              f"judge={score:.2f} ({'pass' if judge_pass(score) else 'fail'}) "
              f"words={words} {mark}")
    r = audit()
    print(f"cases: {len(CASES)}")
    print(f"judge-human agreement: {r['agreement']:.3f}")
    print(f"verbosity bias: verbose wrong answers (n={r['verbose_wrong_n']}) "
          f"mean judge score {r['verbose_wrong_mean']:.3f} vs concise correct "
          f"answers (n={r['concise_right_n']}) mean {r['concise_right_mean']:.3f}")
    biased = r["verbose_wrong_mean"] > r["concise_right_mean"]
    print(f"bias detected: {biased} — the judge rewards length, not correctness")
    print("judgeaudit demo complete")


if __name__ == "__main__":
    main()
