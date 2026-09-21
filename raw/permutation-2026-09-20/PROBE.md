# Permutation-invariance probe — rule frozen 2026-09-20 before the run
- Corpus: ASSAY-001 Banking77 test split (pinned; CORPUS.sha256). Slice: first 300 items in file order. No selection.
- Treatment: same request as ASSAY-001 (same instructions, `jev-latest`, null criteria) with the 77 options in a seeded random order (Python `random.Random(20260920)`, fresh shuffle per item).
- Control: first 50 items re-asked in the ORIGINAL option order (Jev's own drift, same day).
- Comparison target: the sealed 2026-09-18 responses (raw/run/banking77/responses.jsonl).
- Metrics: flip rate (choice differs from sealed) for treatment and control; accuracy of flipped vs stable items (sealed answer and re-ask answer, vs label); share of flips where either answer's p(choice) < 0.9 ("a 0.9 floor would have refused"); |Δp| distribution on stable items.
- One pass. No retries beyond the harness's 429/529 backoff. Everything logged. Cost cap ~350 calls.
- This is a probe for PBB §3b `permutation_invariance`; it is not an ASSAY engagement and is not pre-registered as one.
