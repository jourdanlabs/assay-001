Write a single self-contained Python 3 script (standard library + numpy only; NO other imports) named rescore.py that scores a JSONL file of model responses. Print JSON only. Do not explain.

INPUT: argv[1] = path to responses.jsonl; argv[2] = path to a JSON file containing a list of label strings (the full option set, K options).
Each line of responses.jsonl is a JSON object: {"id": str, "label": str, "response": {"status": int, "ms": float|null, "attempt": int, "body": {"answers": {"intent": {"type": str, "choice": str, "probabilities": {option: float, ...}, "confidence": float}}}}}

RULES:
1. Skip records where response.status != 200 (count them as non_200).
2. Type-safety check per 200 record; a record has a violation if ANY of: answers.intent missing or not an object; type != "choice"; choice not in the label set; probabilities missing/not an object; probabilities keys != the label set exactly; any probability not a number or outside [0,1]; abs(sum(probabilities)-1) > 0.02; confidence not a number or outside [0,1]. Count violations; exclude violating records from calibration.
3. For each non-violating record: correct = 1 if choice == label else 0; p = probabilities[choice].
4. ECE: 10 equal-width bins over p on (0,1]: bin i covers (i/10, (i+1)/10], except bin 0 covers [0, 0.1]. ECE = sum over bins of (n_bin/N) * |mean_accuracy_bin - mean_p_bin|. MCE = max over bins of that absolute gap.
5. Multiclass Brier = mean over records of sum over all K options of (p_k - y_k)^2 where y_k is 1 for the true label else 0.
6. Accuracy = mean(correct).
7. Latency: over 200 records with attempt == 1 and ms not null: median, 95th and 99th percentiles of ms (numpy percentile, default linear).
8. argmax_exceptions: count of non-violating records where probabilities[choice] < max(probabilities.values()) - 1e-9.

OUTPUT (print exactly this JSON object, keys in this order): {"records": int, "non_200": int, "scored": int, "violations": int, "accuracy": float(4dp), "ECE": float(4dp), "MCE": float(4dp), "Brier": float(4dp), "latency_median": float(1dp), "latency_p95": float(1dp), "latency_p99": float(1dp), "argmax_exceptions": int}
