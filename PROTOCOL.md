# ASSAY Engagement 001 — TypeSafe Jev: pre-registered verification protocol

**Subject:** Jev (TypeSafe AI, "System One" model, announced 2026-09-15)
**Auditor:** ASSAY, a JourdanLabs verification practice · **Fee:** none — unsolicited, self-initiated
**Protocol author:** Pan 🐦‍⬛🔑 · **Frozen:** 2026-09-17, **before any query has been sent to the model** (access granted 2026-09-17 via console.typesafe.ai; no key has been used)
**Publication:** whatever this returns publishes at donttrustme.ai, wins and losses drawn the same size. TypeSafe gets no edit and no veto. They are invited to reproduce it.

🐦‍⬛ + 🔑

---

## 0 — The rule this protocol lives under

No number below is measured yet. This document exists so that nobody — including us — can say the method was chosen after the result. The SHA-256 of this file at freeze is recorded in `FREEZE.sha256` beside it and posted publicly before the first API call. If the protocol changes after freeze, the change is an **amendment**, numbered, dated, published, with the reason — never a silent edit.

## 1 — The claims under test (verbatim from typesafe.ai/blog/introducing-system-one-models-and-jev, retrieved 2026-09-15)

| # | Claim, verbatim | Type | Testable? |
|---|---|---|---|
| C1 | *"All answers are accompanied with calibrated probabilities and confidence scores."* and *"Calibrated: higher confidence means higher accuracy."* | calibration | **Yes — the headline test** |
| C2 | *"The model never makes type errors."* — *"This would be an easy thing to falsify with just a single counter-example, but it is mathematically impossible."* | type safety | **Yes — single counter-example suffices** |
| C3 | *"End-to-end response time is 70ms–500ms"* | latency | Yes, as observed from our network; reported as-observed with our location stated, never as a refutation |

**Explicitly NOT under test:** "can't hallucinate" (they do not make that claim; refusing a claim someone didn't make is a strawman) · "40–400× cheaper" (a pricing statement TypeSafe already flags as possibly subsidized; not a technical claim) · any accuracy comparison against frontier LLMs (their own evals do that against model-consensus labels; we don't repeat their method).

## 2 — Corpora (third-party, human-labeled, pinned before access)

Jev's stated task types are classify / route / score / extract with up to 255 choices. We test **route/classify**, where human ground truth exists.

| Corpus | What | Labels | Classes | Split used | Pin |
|---|---|---|---|---|---|
| **Banking77** (PolyAI) | customer-banking queries → intent | human-annotated | 77 | official `test` (3,080 items) | HF `PolyAI/banking77` @ `90d4e2ee5521c04fc1488f065b8b083658768c57`, CC-BY-4.0 |
| **CLINC150** (`clinc_oos`, `plus` config) | assistant queries → intent, incl. an **out-of-scope** class | human-annotated | 150 + OOS | official `test` (5,500 items incl. 1,000 OOS) | HF `clinc/clinc_oos` @ `155b9c710419136e17307b80d0a13e68cd46b4ec`, CC-BY-3.0 |

Both are downloaded at the pinned revision, SHA-256 of every file recorded in `CORPUS.sha256` **before** the first query. We did not build either corpus. We will not edit a label.

**Contamination caveat, stated now:** both corpora are public and old; they may be in Jev's training data. That inflates *accuracy* and does not invalidate the *calibration* measurement: if the model reports 0.9 and is right 90% of the time on this distribution, it is calibrated on this distribution. Accuracy is reported but is not the verdict. CLINC's OOS class is included specifically because a calibrated model must express low confidence there.

## 3 — Method

**One run per corpus.** No retries, no prompt iteration, no second pass. The schema is defined once:
- Output type: single choice from the corpus's label set (77 or 151 choices) — inside Jev's stated 255-choice limit.
- Input: the query text only. No few-shot examples, no label descriptions beyond the label names as published in the corpus.
- Recorded per item: request JSON, response JSON verbatim, confidence/probability as returned, wall-clock latency (ms), timestamp, HTTP status.
- Temperature / sampling: Jev's defaults. Any parameter we set is logged.

**Metrics, declared now:**
- **C1 calibration:** Expected Calibration Error (ECE) with 10 equal-width confidence bins, plus Maximum Calibration Error, plus Brier score, plus a reliability diagram (published). **Pass criterion, fixed now: ECE ≤ 0.05 on both corpora.** Above 0.05 on either = the calibration claim as stated does not hold on that corpus. Also reported: accuracy at each confidence bin; behavior on CLINC OOS (mean confidence assigned to out-of-scope items).
- **C2 type safety:** every response parsed against the declared schema. **Pass criterion: 0 schema violations across all 8,580 responses.** One violation = the claim fails (their own standard).
- **C3 latency:** median / p95 / p99 of observed end-to-end ms from Plano, TX, reported with the network path stated. No pass/fail — it's an observation.

**Positive control (the harness must be able to fail):** before scoring Jev, the scorer is run on (a) a uniform-random classifier with uniform confidence 1/K — expected ECE ≈ 0, accuracy ≈ 1/K; and (b) an always-confident (1.0) random classifier — expected ECE ≈ 1−1/K. Both results published. If the scorer doesn't produce those, we don't publish anything.

## 4 — What may be said afterward

- If ECE ≤ 0.05 on both: *"On Banking77 and CLINC150, Jev's confidence scores were calibrated within ECE 0.0x; higher confidence meant higher accuracy."* — with the contamination caveat attached.
- If not: the number, the diagram, and the sentence *"the calibration claim as stated does not hold on [corpus]"* — and nothing stronger.
- Type errors: the count. Zero or not zero.
- **Never:** "Jev is worse/better than [LLM]" · any accuracy number without the contamination caveat · any claim about tasks we didn't run (extract, score) · any word about hallucination.

## 5 — Who does what (three-leg gate)

- **Harness:** built by the build lane (Toph or Tifa), from this protocol, before access is used. No model in the scorer.
- **Run:** once, by the builder, with Captain's key in the harness environment — the key never appears in a chat, a commit, or a receipt.
- **Gate:** Pan re-scores from the raw response JSONs with an independent scorer, checks the corpus hashes, checks the freeze hash, checks the positive controls.
- **Call:** Captain. Then it publishes.

## 6 — Receipt

`ASSAY-001/` — `PROTOCOL.md` (this file) · `FREEZE.sha256` · `CORPUS.sha256` · `controls/` · `raw/` (every request/response) · `scores.json` · `reliability-*.png` · `REPORT.md` · `RERUN.sh`. Every finding cites an item id. The report ends with the limit clause: *A result applies to the artifacts and criteria examined. It is not a statement about Jev on any other task or corpus.*

**The chamber holds.** 🐦‍⬛ + 🔑
