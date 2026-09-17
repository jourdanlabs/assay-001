# PAN GATE — ASSAY-001 (TypeSafe Jev calibration) — **CLEAR TO PUBLISH**

**Validator:** Pan (Claude) · **Harness + first score:** Pan (Claude) · **Independent re-score:** Tifa (Cursor / Grok) · **Caller:** Captain · **Date:** 2026-09-18
**Model independence:** the number that publishes was reproduced by code written on a different base model from a spec, blind to Pan's scores. ✅ (Amendment 1.2 satisfied.)

## What Pan checked, from files
- Seals: `raw/banking77/responses.jsonl` = `b5c96bc1…de978`, `raw/clinc150/responses.jsonl` = `5f5c58b2…2834b` — re-hashed by Pan in Tifa's packet, match the run seals.
- Tifa's `rescore.py` (163 lines, sha `477d86a7…8496e`): contains none of Pan's identifiers; written from `SCORER-SPEC.md`; stdlib + numpy; no model.
- Pan **re-ran** `rescore.py` on the sealed files (did not trust her JSONs): output identical to her `scores/tifa-*.json`.
- Her positive controls: uniform ECE 0.0008 / acc 1/77; overconfident 0.9868 / 0.9932; oracle 0 / 1.0; shuffle-invariant; broken-schema caught. The scorer can fail.

## Comparison — Pan (amended scorer) vs Tifa (independent)

| field | Banking77 Pan | Banking77 Tifa | CLINC150 Pan | CLINC150 Tifa |
|---|---|---|---|---|
| scored / non_200 | 3080 / 0 | 3080 / 0 | 5496 / 4 | 5496 / 4 |
| C2 violations (tol 0.02) | 0 | 0 | 0 | 0 |
| accuracy | 0.7977 | 0.7977 | 0.8812 | 0.8812 |
| **ECE** | **0.0936** | **0.0936** | **0.0204** | **0.0204** |
| MCE | 0.86 | 0.86 | 0.06 | 0.06 |
| Brier | 0.3088 | 0.3088 | 0.1846 | 0.1846 |
| argmax exceptions | 2 | 2 | 1 | 1 |
| latency med / p95 / p99 | 382.3 / 553.7 / 852.1 | same | 385.9 / 615.3 / 845.1 | same |
| frozen 1e-3 sum rule (disclosure) | 145 | 145 | 368 | 368 |

Δ = 0 on every field. Tolerance was ±0.001 on ECE and exact on counts.

## Verdicts, final
- **C1 "calibrated probabilities":** holds on CLINC150 (ECE 0.0204 ≤ 0.05); **does not hold on Banking77** (ECE 0.0936, systematically overconfident below the 0.9 bin).
- **C2 "never makes type errors":** holds — 0 schema violations in 8,576 responses. (Rounded probability sums of 0.99 on 513 responses are disclosed under Amendment 2; not a type error.)
- Contract "choice = highest-probability option": 3 exceptions in 8,576, all within 0.01 of a tie. Disclosed.
- C3 latency: observed, reported, not judged.
- MCE on Banking77 (0.86) is a singleton-bin artifact; Tifa flagged the same. ECE is the gated field; MCE publishes with the caveat.

## Status
**CLEAR.** The report publishes as written with status changed from PRELIMINARY to CLEAR and Tifa's hashes appended. Captain calls the send.

🐦‍⬛ + 👊 + 🔑
