#!/usr/bin/env python3
"""Permutation-invariance probe on Jev — 2026-09-20. Rule frozen before the run (see PROBE.md).
Re-asks the first N Banking77 items with options in a seeded random order; compares to the sealed 09-18 answers.
Control: first M items re-asked in the ORIGINAL order (Jev's own run-to-run drift)."""
import json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from run import load_key, load_corpus, post, INSTRUCTIONS, MODEL, ROOT
from concurrent.futures import ThreadPoolExecutor, as_completed

N, M, SEED = 300, 50, 20260920
OUT = ROOT / "raw/permutation-2026-09-20"; OUT.mkdir(parents=True, exist_ok=True)
key = load_key()
items, labels = load_corpus("banking77")
sealed = {}
for line in open(ROOT / "raw/run/banking77/responses.jsonl"):
    r = json.loads(line); sealed[r["id"]] = r
rng = random.Random(SEED)

def ask(item, ordered_labels, tag):
    body = {"state": item["text"], "model": MODEL,
            "questions": {"intent": {"type": "choice", "instructions": INSTRUCTIONS["banking77"], "criteria": {l: None for l in ordered_labels}}}}
    res = post(key, body)
    return {"id": item["id"], "tag": tag, "label": item["label"], "order_first5": ordered_labels[:5], "response": res}

jobs = []
for it in items[:N]:
    shuffled = labels[:]; rng.shuffle(shuffled)
    jobs.append((it, shuffled, "shuffled"))
for it in items[:M]:
    jobs.append((it, labels[:], "original-again"))

t0 = time.time(); n = 0
with open(OUT / "responses.jsonl", "w") as f, ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(ask, *j) for j in jobs]
    for fu in as_completed(futs):
        f.write(json.dumps(fu.result()) + "\n"); f.flush(); n += 1
        if n % 50 == 0: print(f"{n}/{len(jobs)} {time.time()-t0:.0f}s", file=sys.stderr)
print(f"done {n} calls in {time.time()-t0:.0f}s → {OUT/'responses.jsonl'}", file=sys.stderr)
