#!/usr/bin/env python3
"""ASSAY-001 — Jev calibration run. One Choice question per corpus item, one pass, everything logged.

Protocol: pan-cc/handoffs/ASSAY-001-JEV-CALIBRATION-PROTOCOL-2026-09-17.md (frozen, sha f8ce3f5b…a09b48)
Key: read from ~/.config/typesafe/api_key or $TYPESAFE_API_KEY. Never printed, never written.
"""
import json, os, sys, time, hashlib, argparse, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

INSTRUCTIONS = {
    "banking77": "Which banking intent does this customer message express? Choose exactly one.",
    "clinc150": "Which intent does this user request express? Choose exactly one. Choose oos if it matches none of the others.",
}

def load_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    p = Path.home() / ".config" / "typesafe" / "api_key"
    if not k and p.exists():
        k = p.read_text().strip()
    if not k:
        sys.exit("no API key: put it in ~/.config/typesafe/api_key (chmod 600) or $TYPESAFE_API_KEY")
    return k

def load_corpus(name):
    if name == "banking77":
        df = pd.read_csv(ROOT / "corpus/banking77/test.csv")
        labels = json.load(open(ROOT / "corpus/banking77/categories.json"))
        items = [{"id": f"b77-{i:04d}", "text": r.text, "label": r.category} for i, r in enumerate(df.itertuples())]
    elif name == "clinc150":
        df = pd.read_parquet(ROOT / "corpus/clinc150/test.parquet")
        names = json.load(open(ROOT / "corpus/clinc150/intent_names.json"))
        labels = [names[str(i)] for i in range(len(names))]
        items = [{"id": f"c150-{i:04d}", "text": r.text, "label": names[str(r.intent)]} for i, r in enumerate(df.itertuples())]
    else:
        raise SystemExit(name)
    assert all(it["label"] in labels for it in items)
    return items, labels

def make_request(name, item, labels):
    return {
        "state": item["text"],
        "model": MODEL,
        "questions": {"intent": {"type": "choice", "instructions": INSTRUCTIONS[name], "criteria": {l: None for l in labels}}},
    }

def post(key, body, max_tries=8):
    data = json.dumps(body).encode()
    delay = 1.0
    for attempt in range(1, max_tries + 1):
        req = urllib.request.Request(API, data=data, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "ASSAY-001/1.0"})
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read(); ms = (time.perf_counter() - t0) * 1000
                return {"status": r.status, "ms": round(ms, 1), "attempt": attempt, "body": json.loads(raw)}
        except urllib.error.HTTPError as e:
            ms = (time.perf_counter() - t0) * 1000
            text = e.read().decode(errors="replace")
            if e.code in (429, 529) and attempt < max_tries:
                time.sleep(delay); delay = min(delay * 2, 30); continue
            return {"status": e.code, "ms": round(ms, 1), "attempt": attempt, "error": text[:2000]}
        except Exception as e:  # network
            if attempt < max_tries:
                time.sleep(delay); delay = min(delay * 2, 30); continue
            return {"status": 0, "ms": None, "attempt": attempt, "error": repr(e)[:2000]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", choices=["banking77", "clinc150"])
    ap.add_argument("--limit", type=int, default=0, help="smoke test: first N items, written to raw/smoke/")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    items, labels = load_corpus(a.corpus)
    if a.limit: items = items[: a.limit]
    outdir = ROOT / "raw" / ("smoke" if a.limit else "run") / a.corpus
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"corpus": a.corpus, "n": len(items), "labels": len(labels), "model": MODEL, "instructions": INSTRUCTIONS[a.corpus],
                "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "protocol_sha256": "f8ce3f5b72abd4f48b8da0efdd1769d12f5e111d6e905b298cf0251bc4a09b48",
                "corpus_sha256": (ROOT / "CORPUS.sha256").read_text(), "smoke": bool(a.limit)}
    (outdir / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    if a.dry_run:
        print(json.dumps(make_request(a.corpus, items[0], labels), indent=1)[:1200]); return

    key = load_key()
    lock = threading.Lock(); done = 0; fails = 0
    def work(item):
        body = make_request(a.corpus, item, labels)
        res = post(key, body)
        rec = {"id": item["id"], "text": item["text"], "label": item["label"], "request": body, "response": res, "ts": time.time()}
        return rec
    log = open(outdir / "responses.jsonl", "a")
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(work, it): it for it in items}
        for f in as_completed(futs):
            rec = f.result()
            with lock:
                log.write(json.dumps(rec) + "\n"); log.flush(); done += 1
                if rec["response"]["status"] != 200: fails += 1
                if done % 100 == 0 or done == len(items):
                    print(f"{a.corpus}: {done}/{len(items)}  non-200: {fails}", flush=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z"); manifest["non_200"] = fails
    (outdir / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    h = hashlib.sha256((outdir / "responses.jsonl").read_bytes()).hexdigest()
    (outdir / "responses.sha256").write_text(f"{h}  responses.jsonl\n")
    print("sealed", h)

if __name__ == "__main__":
    main()
