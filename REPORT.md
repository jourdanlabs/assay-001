# ASSAY-001 — REPORT · TypeSafe Jev (`jev-latest`) · calibration and type safety

**Run:** 2026-09-18 (Thursday), one pass per corpus, from a MacBook Pro in The Woodlands, TX. **Protocol frozen 2026-09-17** (`f8ce3f5b…a09b48`, commit `7d6b171`) and **Amendment 1** (`9cd8489`) before any query. **Amendment 2** (below) after the run, numbered and published, with both scorer results shown.
**Auditor:** ASSAY / JourdanLabs · **Harness + this scoring:** Pan (Claude) · **Independent re-score required before publication:** a second party on a different base model must reproduce the numbers below from `raw/run/*/responses.jsonl` (Amendment 1.2). **Status: PRELIMINARY until that re-score lands.**
**Cost:** 0.01 USD-ish (input at $0.042/MTok; output free). Every request and response: `raw/run/<corpus>/responses.jsonl`, sealed — banking77 `b5c96bc1…de978`, clinc150 `5f5c58b2…2834b`.

## Verdicts

| Claim | Banking77 (77 intents, n=3080) | CLINC150 (150 intents + oos, n=5496) |
|---|---|---|
| **C1 — "calibrated probabilities"** (ECE ≤ 0.05) | **ECE 0.0936 — DOES NOT HOLD** · MCE 0.2667 (frozen scorer) · Brier 0.3088 · accuracy 0.7977 | **ECE 0.0204 — HOLDS** · MCE 0.06 · Brier 0.1846 · accuracy 0.8812 |
| **C2 — "never makes type errors"** | **0 schema violations in 3080** (Amendment 2) · frozen 1e-3 sum rule: 145 rounding cases, see A2 | **0 schema violations in 5496** · frozen rule: 368 rounding cases |
| Contract: `choice` is the highest-probability option | 2 exceptions (both within 0.01 of a tie) | 1 exception (within 0.01 of a tie) |
| C3 — observed latency (ms, end-to-end, our network) | median 382.3 · p95 553.7 · p99 852.1 | median 385.9 · p95 615.3 · p99 845.1 |

**What may be said:** *On CLINC150, Jev's chosen-option probabilities were calibrated (ECE 0.0204); on Banking77 they were not (ECE 0.0936, systematically overconfident below the 0.9 bin). Across 8,576 responses there were zero type errors.* Both sentences travel together.

**What may not be said:** "Jev is calibrated" unqualified · "Jev is not calibrated" unqualified · any accuracy number as a quality verdict (contamination caveat, §2 of the protocol) · anything about tasks not run (score, extract, noul).

## C1 detail — reliability (probability of chosen option, 10 bins)

**Banking77** — overconfident in every populated bin from 0.3 upward; the 0.9–1.0 bin (69% of items) is 5.9 points over.

| bin | n | mean prob | accuracy | gap |
|---|---|---|---|---|
| (0.1,0.2] | 1 | 0.14 | 1.0 | 0.86 |
| (0.2,0.3] | 6 | 0.275 | 0.1667 | 0.1083 |
| (0.3,0.4] | 40 | 0.3668 | 0.2 | 0.1668 |
| (0.4,0.5] | 92 | 0.4652 | 0.337 | 0.1283 |
| (0.5,0.6] | 176 | 0.5526 | 0.358 | 0.1946 |
| (0.6,0.7] | 181 | 0.654 | 0.5083 | 0.1457 |
| (0.7,0.8] | 206 | 0.755 | 0.5874 | 0.1677 |
| (0.8,0.9] | 249 | 0.8614 | 0.6667 | 0.1947 |
| (0.9,1.0] | 2129 | 0.9857 | 0.9272 | 0.0585 |

**CLINC150** — tracks the diagonal within 2.5 points in every bin with n ≥ 50.

| bin | n | mean prob | accuracy | gap |
|---|---|---|---|---|
| (0.2,0.3] | 14 | 0.2743 | 0.2143 | 0.06 |
| (0.3,0.4] | 59 | 0.3751 | 0.3898 | 0.0147 |
| (0.4,0.5] | 162 | 0.4603 | 0.4753 | 0.015 |
| (0.5,0.6] | 278 | 0.5526 | 0.5612 | 0.0086 |
| (0.6,0.7] | 279 | 0.6533 | 0.6667 | 0.0134 |
| (0.7,0.8] | 332 | 0.7589 | 0.756 | 0.0029 |
| (0.8,0.9] | 510 | 0.8605 | 0.851 | 0.0095 |
| (0.9,1.0] | 3862 | 0.9863 | 0.9614 | 0.0249 |

**Out-of-scope (CLINC `oos`, n=1000):** accuracy 0.723 · mean chosen-option probability 0.7903 · mean `confidence` 0.7799 on oos vs 0.9176 in-scope. The model does express lower certainty on out-of-scope inputs; it still commits at ~0.79 on average.

**Jev's own `confidence` field** (secondary, not gated): ECE 0.088 (B77) / 0.0217 (CLINC). Accuracy by decile is not strictly monotone on either corpus — the field saturates at 1.00 across the top three deciles on Banking77 (accuracy 0.97–0.98 there).

Banking77 confidence deciles:
| decile | n | mean confidence | accuracy |
|---|---|---|---|
| 1 | 308 | 0.4784 | 0.3344 |
| 2 | 308 | 0.6713 | 0.5422 |
| 3 | 308 | 0.8269 | 0.6396 |
| 4 | 308 | 0.9245 | 0.7955 |
| 5 | 308 | 0.9664 | 0.8604 |
| 6 | 308 | 0.9869 | 0.9253 |
| 7 | 308 | 0.9975 | 0.9513 |
| 8 | 308 | 1.0 | 0.9838 |
| 9 | 308 | 1.0 | 0.9481 |
| 10 | 308 | 1.0 | 0.9968 |

## Amendment 2 (2026-09-18, after the run — the reason it's numbered)

The frozen C2 rule required `probabilities` to sum to 1 within 1e-3. Jev returns probabilities **rounded to two decimals**; with 77–151 options the rounded sum is 0.99 on 145 + 368 responses (never 1.01, never below 0.99). That is rounding, not a type error, and under the frozen rule those items would also have been *excluded from the calibration score* — which would have made C1 look slightly better on Banking77 (ECE 0.0904 on the 2,935 survivors vs 0.0936 on all 3,080). **Amendment 2:** sum tolerance 0.02; all items scored; the observed sum range published (0.99–1.0). Both scorer outputs are committed (`scores/jev-frozen-*.json`, `scores/jev-*.json`). The verdicts do not change under either rule. The `choice`-is-argmax check moved from C2 to its own row: it's a documentation contract, not a type.

## Disclosures

- **4 CLINC items were not scored** (`c150-2893..2896`): DNS resolution failed **on the auditor's laptop** during the run (the operator's wifi dropped). Auditor-side, not Jev. Excluded, not retried — the protocol says one run. n=5,496 of 5,500.
- **Smoke test:** 3 items per corpus were sent before the run to confirm connectivity (`raw/smoke/`), excluded from scoring, disclosed per Amendment 1.3.
- **Contamination:** both corpora are public and old (2020, 2019). Accuracy is reported, not judged. Calibration on this distribution is what was measured.
- **Latency** includes the public internet from central Texas; TypeSafe's "70–500 ms" is consistent with our median and not with our tails. Reported, not judged.
- **Builder = scorer = Pan** for this preliminary. Not publishable alone (Amendment 1.2).

## The limit
A result applies to the artifacts and criteria examined — `jev-latest` on 2026-09-18, Choice questions with null option descriptions, these two corpora. It is not a statement about Jev on any other task, corpus, or day.

🐦‍⬛ + 🔑
