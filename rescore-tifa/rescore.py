#!/usr/bin/env python3
"""Independent ASSAY-001 scorer. Stdlib + numpy only. Print JSON only."""
import json
import sys

import numpy as np


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def bin_index(p):
    if p <= 0.1:
        return 0
    for i in range(1, 10):
        if p <= (i + 1) / 10.0:
            return i
    return 9


def r4(x):
    return float(f"{x:.4f}")


def r1(x):
    return float(f"{x:.1f}")


def main():
    if len(sys.argv) != 3:
        sys.exit(2)
    jsonl_path = sys.argv[1]
    labels_path = sys.argv[2]
    with open(labels_path, "r", encoding="utf-8") as f:
        labels = json.load(f)
    if not isinstance(labels, list) or not labels:
        sys.exit(2)
    label_set = set(labels)
    if len(label_set) != len(labels):
        sys.exit(2)

    records = 0
    non_200 = 0
    violations = 0
    scored_correct = []
    scored_p = []
    scored_brier = []
    argmax_exceptions = 0
    latencies = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            records += 1
            rec = json.loads(line)
            response = rec.get("response")
            if not isinstance(response, dict) or response.get("status") != 200:
                non_200 += 1
                continue

            attempt = response.get("attempt")
            ms = response.get("ms")
            if attempt == 1 and is_number(ms):
                latencies.append(float(ms))

            body = response.get("body")
            answers = body.get("answers") if isinstance(body, dict) else None
            intent = answers.get("intent") if isinstance(answers, dict) else None
            bad = False
            if not isinstance(intent, dict):
                bad = True
            else:
                choice = intent.get("choice")
                probs = intent.get("probabilities")
                conf = intent.get("confidence")
                if intent.get("type") != "choice":
                    bad = True
                if not isinstance(choice, str) or choice not in label_set:
                    bad = True
                if not isinstance(probs, dict):
                    bad = True
                else:
                    if set(probs.keys()) != label_set:
                        bad = True
                    values = []
                    for v in probs.values():
                        if not is_number(v) or v < 0.0 or v > 1.0:
                            bad = True
                        else:
                            values.append(float(v))
                    if values and abs(sum(values) - 1.0) > 0.02:
                        bad = True
                if not is_number(conf) or conf < 0.0 or conf > 1.0:
                    bad = True

            if bad:
                violations += 1
                continue

            choice = intent["choice"]
            probs = {k: float(v) for k, v in intent["probabilities"].items()}
            true_label = rec.get("label")
            correct = 1 if choice == true_label else 0
            p_choice = probs[choice]
            scored_correct.append(correct)
            scored_p.append(p_choice)
            brier = 0.0
            for lab in labels:
                y = 1.0 if lab == true_label else 0.0
                brier += (probs[lab] - y) ** 2
            scored_brier.append(brier)
            if p_choice < max(probs.values()) - 1e-9:
                argmax_exceptions += 1

    n = len(scored_correct)
    if n == 0:
        accuracy = ece = mce = brier = 0.0
    else:
        accuracy = float(np.mean(scored_correct))
        brier = float(np.mean(scored_brier))
        bin_acc = [[] for _ in range(10)]
        bin_p = [[] for _ in range(10)]
        for c, p in zip(scored_correct, scored_p):
            i = bin_index(p)
            bin_acc[i].append(c)
            bin_p[i].append(p)
        ece = 0.0
        gaps = []
        for i in range(10):
            if not bin_acc[i]:
                continue
            gap = abs(float(np.mean(bin_acc[i])) - float(np.mean(bin_p[i])))
            ece += (len(bin_acc[i]) / n) * gap
            gaps.append(gap)
        mce = max(gaps) if gaps else 0.0

    if latencies:
        q = np.percentile(np.asarray(latencies, dtype=float), [50, 95, 99])
        lat_med, lat_p95, lat_p99 = float(q[0]), float(q[1]), float(q[2])
    else:
        lat_med = lat_p95 = lat_p99 = 0.0

    out = {
        "records": records,
        "non_200": non_200,
        "scored": n,
        "violations": violations,
        "accuracy": r4(accuracy),
        "ECE": r4(ece),
        "MCE": r4(mce),
        "Brier": r4(brier),
        "latency_median": r1(lat_med),
        "latency_p95": r1(lat_p95),
        "latency_p99": r1(lat_p99),
        "argmax_exceptions": argmax_exceptions,
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
