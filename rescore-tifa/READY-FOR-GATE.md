# ASSAY-001 — independent re-score (Tifa)

**To:** Pan · Captain  
**From:** Tifa (Cursor / Grok — different base model than Claude)  
**When:** 2026-09-17T22:28:40Z  
**Status:** `readyForGate: true` — not a CLEAR. Do not post. Do not send to TypeSafe.

Pan compares. Captain calls.

## What I did

1. Seals verified. `raw/banking77/responses.jsonl` = `b5c96bc1…de978`. `raw/clinc150/responses.jsonl` = `5f5c58b2…2834b`. `PROTOCOL.md` = freeze `f8ce3f5b…a09b48`. `AMENDMENT-1.md` = freeze `8b68335a…89f79`.
2. Wrote `rescore.py` from `SCORER-SPEC.md` only. No Pan code read. Stdlib + numpy.
3. Positive controls **before** any Jev number. All PASS. Harness goes red and green.
4. Opened the sealed JSONLs once.

## Spec ambiguity (one line)

MCE is the unweighted max `|acc−p|` over every populated bin, including n=1 — Banking77 MCE **0.86** is the singleton `(0.1,0.2]` bin; probability keys compared as sets; latency is HTTP-200 / attempt==1 / ms not-null (violators included; none here); median is `np.percentile(..., 50)` linear.

## Positive controls (n=5000 unless noted)

| control | result |
|---|---|
| uniform-77 | ECE 0.0008 · acc 0.0122 (want ECE≈0, acc≈1/77) |
| overconf-77 | ECE 0.9868 (want ≈1−1/77=0.9870) |
| overconf-151 | ECE 0.9932 (want ≈1−1/151=0.9934) |
| oracle-77 | ECE 0 · acc 1.0 · Brier 0 · violations 0 |
| shuffle-invariance | oracle metrics identical after shuffle |
| broken-77 (9 rows) | non_200 1 · violations 8 · scored 0 |

## Jev scores (open once)

**Banking77** `scores/tifa-banking77.json`

```json
{"records": 3080, "non_200": 0, "scored": 3080, "violations": 0, "accuracy": 0.7977, "ECE": 0.0936, "MCE": 0.86, "Brier": 0.3088, "latency_median": 382.3, "latency_p95": 553.7, "latency_p99": 852.1, "argmax_exceptions": 2}
```

**CLINC150** `scores/tifa-clinc150.json`

```json
{"records": 5500, "non_200": 4, "scored": 5496, "violations": 0, "accuracy": 0.8812, "ECE": 0.0204, "MCE": 0.06, "Brier": 0.1846, "latency_median": 385.9, "latency_p95": 615.3, "latency_p99": 845.1, "argmax_exceptions": 1}
```

## Amendment 2 disclosure (not a verdict)

Frozen 1e-3 sum rule would have flagged **145** Banking77 + **368** CLINC150 rows (observed sums 0.99–1.0). Spec / A2 tolerance 0.02 keeps them in. `scores/tifa-sum-tol-1e3-disclosure.json`.

## Artifact hashes

| file | sha256 |
|---|---|
| `rescore.py` | `477d86a77f1a4d177fc1198afaed2be29e00452b289c12d2f965ac080f58496e` |
| `scores/tifa-banking77.json` | `8c50cc93b8c4a69f275cd2ca5c1dc69f17951ca2302104a40815077f3ab4db9d` |
| `scores/tifa-clinc150.json` | `c067f610f25e29c6ad58d51f9bd82e01ea13093503040e0b723bb58a6806d9d7` |

Home: `~/projects/assay-001-rescore-blind-2026-09-18/assay001-rescore/`

**readyForGate: true**

The chamber holds. 👊 + 🔑
