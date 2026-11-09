# AI Observability in Production — Companion Code (Udemy Course 9)

Working, stdlib-only Python demos for every hands-on lesson of the course.
No API keys, no third-party packages: every mechanic runs offline so students
see what the production tools actually compute. One shared module,
`obscommon.py`, carries the deterministic synthetic telemetry dataset for a
support-chat AI service, the token price table, and the percentile/mean
helpers every package grades itself with.

## Run the full validation
```
python validate.py
```
Expected final line: `OVERALL: PASS`.

## Packages (one per DEMO lesson)
| Package | Lesson | What it shows |
|---|---|---|
| blindspot | 5 | Infra metrics stay green while answer quality collapses after a silent model change |
| logline | 9 | Structured JSON logs with a fixed schema — validated, with secrets/PII redacted |
| traceweave | 13 | A span tree for one agent request: total, critical path, slowest and failed spans |
| promptwatch | 17 | Prompt version registry: diff two versions, grade quality/cost, flag the regression |
| judgeaudit | 21 | Audit the LLM judge against human labels — agreement and planted verbosity bias |
| tokenledger | 25 | Token cost attribution by tenant/feature/prompt version, plus retry-storm waste |
| p99hunt | 29 | Per-stage p50/p95/p99 latency profiling — the dominant tail stage, named |
| decayradar | 33 | Baseline vs current windows: quality drift and hallucination rise vs thresholds |
| pagewise | 37 | SLO + error-budget math; naive threshold paging vs burn-rate paging, simulated |
| culprit | 45 | Multi-agent trace graph: blame the first agent whose output went wrong |
| watchstack | 50/51 | The capstone observability stack, end to end, with its ship verdict |

## Lesson tags
Each DEMO lesson is tagged in this repo: `lXX-start` (code before the lesson's
build) and `lXX-finish` (the exact code the lesson ships). Tags are added as
each DEMO lesson is produced; the pilot (Lesson 1) is a theory lesson and
carries no tag.
