#!/usr/bin/env python3
"""ASSAY-001 scorer. Deterministic. No model. Reads raw responses.jsonl, writes scores.json + reliability diagram.

Metrics declared in the frozen protocol:
  C1 calibration — ECE (10 equal-width bins) on the probability of the chosen option (max-prob); MCE; multiclass Brier;
                   reliability diagram; accuracy per bin. Secondary: accuracy per decile of Jev's own `confidence` field.
                   Pass: ECE <= 0.05.
  C2 type safety — every 200 response parsed against the declared schema: answer type 'choice', `choice` in label set,
                   `probabilities` has exactly the label set as keys, all in [0,1], sum within 1e-3 of 1, `confidence` in [0,1].
                   Pass: 0 violations.
  C3 latency     — median/p95/p99 of observed ms (successful responses; first attempt only counted as observed).
Also: an input may be scored from a synthetic control file with the same record shape (see controls.py).
"""
import json, sys, math, argparse
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent

def load_labels(corpus):
    if corpus == "banking77":
        return json.load(open(ROOT / "corpus/banking77/categories.json"))
    names = json.load(open(ROOT / "corpus/clinc150/intent_names.json"))
    return [names[str(i)] for i in range(len(names))]

def ece_mce(conf, correct, bins=10):
    conf = np.asarray(conf); correct = np.asarray(correct, dtype=float)
    edges = np.linspace(0, 1, bins + 1); ece = 0.0; mce = 0.0; rows = []
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        m = (conf > lo) & (conf <= hi) if i > 0 else (conf >= lo) & (conf <= hi)
        n = int(m.sum())
        if n == 0:
            rows.append({"bin": f"({lo:.1f},{hi:.1f}]", "n": 0, "conf": None, "acc": None, "gap": None}); continue
        c = float(conf[m].mean()); acc = float(correct[m].mean()); gap = abs(acc - c)
        ece += (n / len(conf)) * gap; mce = max(mce, gap)
        rows.append({"bin": f"({lo:.1f},{hi:.1f}]", "n": n, "conf": round(c, 4), "acc": round(acc, 4), "gap": round(gap, 4)})
    return round(float(ece), 4), round(float(mce), 4), rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", choices=["banking77", "clinc150"])
    ap.add_argument("--input", default=None, help="responses.jsonl (default raw/run/<corpus>/responses.jsonl)")
    ap.add_argument("--tag", default="jev")
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--sum-tol", type=float, default=1e-3, help="frozen: 1e-3. Amendment 2: 0.02 (2-decimal rounding)")
    a = ap.parse_args()
    labels = load_labels(a.corpus); L = set(labels)
    path = Path(a.input) if a.input else ROOT / "raw/run" / a.corpus / "responses.jsonl"
    recs = [json.loads(l) for l in open(path)]

    viol = []; ok = []; latency = []; non200 = 0; argmax_viol = []; sums = []
    for r in recs:
        resp = r["response"]
        if resp.get("status") != 200:
            non200 += 1; continue
        if resp.get("attempt", 1) == 1 and resp.get("ms") is not None: latency.append(resp["ms"])
        ans = (resp.get("body") or {}).get("answers", {}).get("intent")
        v = []
        if not isinstance(ans, dict): v.append("no answer object")
        else:
            if ans.get("type") != "choice": v.append(f"type={ans.get('type')!r}")
            ch = ans.get("choice")
            if ch not in L: v.append(f"choice not in label set: {ch!r}")
            pr = ans.get("probabilities")
            if not isinstance(pr, dict): v.append("probabilities missing")
            else:
                sums.append(sum(pr.values()))
                if set(pr.keys()) != L: v.append(f"probabilities keys != label set (extra={sorted(set(pr)-L)[:3]}, missing={sorted(L-set(pr))[:3]})")
                vals = list(pr.values())
                if any((not isinstance(x, (int, float))) or x < 0 or x > 1 or (isinstance(x, float) and math.isnan(x)) for x in vals): v.append("probability out of [0,1]")
                elif abs(sum(vals) - 1.0) > a.sum_tol: v.append(f"probabilities sum={sum(vals):.5f}")

            cf = ans.get("confidence")
            if not isinstance(cf, (int, float)) or cf < 0 or cf > 1: v.append(f"confidence={cf!r}")
        if v: viol.append({"id": r["id"], "violations": v})
        else:
            if pr[ch] < max(pr.values()) - 1e-9: argmax_viol.append({"id": r["id"], "choice": ch, "p_choice": pr[ch], "argmax": max(pr, key=pr.get), "p_argmax": max(pr.values())})
            ok.append({"id": r["id"], "label": r["label"], "choice": ch, "correct": int(ch == r["label"]),
                       "maxprob": float(ans["probabilities"][ch]), "confidence": float(ans["confidence"]),
                       "p_true": float(ans["probabilities"].get(r["label"], 0.0)), "probs": ans["probabilities"]})

    n = len(ok)
    out = {"corpus": a.corpus, "tag": a.tag, "records": len(recs), "non_200": non200, "scored": n, "labels": len(labels),
           "C2_type_safety": {"sum_tolerance": a.sum_tol, "violations": len(viol), "pass": len(viol) == 0, "examples": viol[:10]},
           "contract_choice_is_argmax": {"violations": len(argmax_viol), "examples": argmax_viol[:10]},
           "probability_sums": {"min": round(min(sums), 4) if sums else None, "max": round(max(sums), 4) if sums else None, "n_not_exactly_1_within_1e-3": int(sum(1 for x in sums if abs(x - 1) > 1e-3))}}
    if n:
        acc = float(np.mean([o["correct"] for o in ok]))
        ece, mce, rows = ece_mce([o["maxprob"] for o in ok], [o["correct"] for o in ok])
        # multiclass Brier: mean over items of sum_k (p_k - y_k)^2
        brier = float(np.mean([sum((p - (1.0 if k == o["label"] else 0.0)) ** 2 for k, p in o["probs"].items()) for o in ok]))
        # secondary: accuracy by decile of Jev's own confidence field
        cf = np.array([o["confidence"] for o in ok]); cr = np.array([o["correct"] for o in ok], dtype=float)
        order = np.argsort(cf); dec = []
        for d in range(10):
            idx = order[d * n // 10:(d + 1) * n // 10]
            if len(idx): dec.append({"decile": d + 1, "n": int(len(idx)), "conf_mean": round(float(cf[idx].mean()), 4), "acc": round(float(cr[idx].mean()), 4)})
        monotone = all(dec[i]["acc"] <= dec[i + 1]["acc"] + 1e-9 for i in range(len(dec) - 1))
        conf_ece, conf_mce, conf_rows = ece_mce(cf, cr)
        out["C1_calibration"] = {"accuracy": round(acc, 4), "ECE_maxprob": ece, "MCE_maxprob": mce, "Brier_multiclass": round(brier, 4),
                                 "pass_ECE_le_0.05": ece <= 0.05, "reliability_bins_maxprob": rows,
                                 "confidence_field": {"ECE": conf_ece, "MCE": conf_mce, "acc_by_decile": dec, "monotone_nondecreasing": monotone, "bins": conf_rows}}
        if a.corpus == "clinc150":
            oos = [o for o in ok if o["label"] == "oos"]; ins = [o for o in ok if o["label"] != "oos"]
            out["C1_calibration"]["oos"] = {"n": len(oos), "acc_oos": round(float(np.mean([o["correct"] for o in oos])), 4) if oos else None,
                                            "mean_maxprob_oos": round(float(np.mean([o["maxprob"] for o in oos])), 4) if oos else None,
                                            "mean_confidence_oos": round(float(np.mean([o["confidence"] for o in oos])), 4) if oos else None,
                                            "mean_confidence_inscope": round(float(np.mean([o["confidence"] for o in ins])), 4) if ins else None,
                                            "acc_inscope": round(float(np.mean([o["correct"] for o in ins])), 4) if ins else None}
    if latency:
        lat = np.array(latency)
        out["C3_latency_ms"] = {"n": int(len(lat)), "median": round(float(np.median(lat)), 1), "p95": round(float(np.percentile(lat, 95)), 1),
                                "p99": round(float(np.percentile(lat, 99)), 1), "min": round(float(lat.min()), 1), "max": round(float(lat.max()), 1),
                                "note": "observed end-to-end from Plano, TX; includes network"}
    (ROOT / "scores").mkdir(exist_ok=True)
    outp = ROOT / "scores" / f"{a.tag}-{a.corpus}.json"
    outp.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "C1_calibration"} | ({"C1": {k: v for k, v in out["C1_calibration"].items() if k not in ("reliability_bins_maxprob", "confidence_field")}} if n else {}), indent=1))
    if n and not a.no_plot:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5, 5)); xs = [r["conf"] for r in rows if r["n"]]; ys = [r["acc"] for r in rows if r["n"]]
        ax.plot([0, 1], [0, 1], "--", color="#999", label="perfect calibration"); ax.plot(xs, ys, "o-", color="#25374b", label=f"{a.tag} · ECE {ece}")
        for r in rows:
            if r["n"]: ax.annotate(str(r["n"]), (r["conf"], r["acc"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
        ax.set_xlabel("probability of chosen option (bin mean)"); ax.set_ylabel("accuracy in bin"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(f"ASSAY-001 · {a.corpus} · n={n}"); ax.legend(loc="upper left", fontsize=8); fig.tight_layout()
        fig.savefig(ROOT / "scores" / f"reliability-{a.tag}-{a.corpus}.png", dpi=160)
    print("wrote", outp)

if __name__ == "__main__":
    main()
