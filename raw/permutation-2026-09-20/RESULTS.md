# Permutation-invariance probe on Jev (`jev-latest`) — results, 2026-09-20

**Status: PROBE.** One pass, 350 calls, 0 errors, 41 s. Rule frozen in PROBE.md (sha256 97bf59c2…) before the run. Not an ASSAY engagement; not pre-registered as one. Slice = first 300 Banking77 test items in file order.

| | n | flips vs sealed 09-18 answer |
|---|---|---|
| options **shuffled** (seed 20260920) | 300 | **16 (5.3%)** |
| options in **original order**, re-asked same day (control) | 50 | **0 (0.0%)** |

**Flipped items (16):** sealed answer correct 9/16 · re-ask correct 4/16 · both wrong 3/16. Mean p(choice) sealed 0.59, re-ask 0.55. **All 16 had p(choice) < 0.9 on both sides; 0 flips with both sides ≥ 0.9.** A 0.9 floor (PBB §3b `calibration_floor`) refuses 16/16. Dominant confusion: `card_arrival` ↔ `card_delivery_estimate`.

**Stable items (284):** accuracy 83.8%. |Δp(choice)| mean 0.049, max 0.38; **81/284 (28.5%) moved by > 0.05** vs 6/50 (12%) in the same-order control. The probability is not order-invariant even when the choice is.

**Read-across:** Running-Dolphins reported 8.7% order flips on a different slice/setup; this probe finds 5.3% under ASSAY-001's exact request shape. Direction agrees; magnitude differs; neither is pre-registered.

**For §3b:** on this corpus the floor alone catches every order flip; `permutation_invariance` is a check on the floor's setting, not a first-line verifier. The Δp finding argues for logging p under two orders and reporting the spread in the receipt.

Raw: `responses.jsonl` (every request/response, both arms). Comparison target: `raw/run/banking77/responses.jsonl` (sealed 09-18).
