#!/usr/bin/env python3
"""ASSAY-001 positive controls — prove the scorer can fail before it scores Jev.

Writes synthetic responses.jsonl files in the exact record shape run.py produces, then score.py scores them.
  uniform-random   : random choice, probabilities uniform 1/K        -> expect ECE ~ 0, accuracy ~ 1/K
  overconfident    : random choice, probability 1.0 on the choice    -> expect ECE ~ 1 - 1/K
  perfect-oracle   : correct choice, probability 1.0                 -> expect ECE ~ 0, accuracy 1.0
  broken-schema    : uniform-random with one probability key dropped -> expect C2 violations > 0
Seeded, deterministic.
"""
import json, random, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from run import load_corpus, make_request

def synth(corpus, mode, seed=1):
    items, labels = load_corpus(corpus); K = len(labels); rng = random.Random(seed)
    out = ROOT / "controls" / corpus; out.mkdir(parents=True, exist_ok=True)
    path = out / f"{mode}.jsonl"
    with open(path, "w") as f:
        for it in items:
            body = make_request(corpus, it, labels)
            if mode == "perfect-oracle": ch = it["label"]
            else: ch = rng.choice(labels)
            if mode == "uniform-random" or mode == "broken-schema":
                probs = {l: 1.0 / K for l in labels}
                # make choice the argmax by a hair so it's a valid record
                probs[ch] += 1e-6; s = sum(probs.values()); probs = {k: v / s for k, v in probs.items()}
                if mode == "broken-schema" and rng.random() < 0.01:
                    probs.pop(rng.choice([l for l in labels if l != ch]))
                conf = 0.0
            else:
                probs = {l: (1.0 if l == ch else 0.0) for l in labels}; conf = 1.0
            resp = {"status": 200, "ms": 100.0, "attempt": 1, "body": {"model": "control", "answers": {"intent": {"type": "choice", "choice": ch, "probabilities": probs, "confidence": conf}}, "usage": {"input_tokens": 0, "output_tokens": 0}}}
            f.write(json.dumps({"id": it["id"], "text": it["text"], "label": it["label"], "request": body, "response": resp, "ts": 0}) + "\n")
    return path

if __name__ == "__main__":
    for corpus in ["banking77", "clinc150"]:
        for mode in ["uniform-random", "overconfident", "perfect-oracle", "broken-schema"]:
            p = synth(corpus, mode)
            r = subprocess.run([sys.executable, str(ROOT / "harness/score.py"), corpus, "--input", str(p), "--tag", f"control-{mode}", "--no-plot"], capture_output=True, text=True)
            j = json.load(open(ROOT / "scores" / f"control-{mode}-{corpus}.json"))
            c1 = j.get("C1_calibration", {}); c2 = j["C2_type_safety"]
            print(f"{corpus:10s} {mode:16s} scored={j['scored']:5d} acc={c1.get('accuracy')} ECE={c1.get('ECE_maxprob')} C2_violations={c2['violations']}")
