import json
import random

# Load all 60 answers
rows = [json.loads(l) for l in open("data/answers.jsonl", encoding="utf-8")]

# Group the two answers by question id
by_q = {}
for r in rows:
    by_q.setdefault(r["id"], {})[r["model"]] = r

# Fixed seed so the random order is the same every time you run this
random.seed(42)

pairs = []
for qid in sorted(by_q):
    a_model, b_model = "llama-3.2-3b", "gpt-oss-120b"
    # Randomly decide which model is shown as "Answer A".
    # This avoids always showing the big model first.
    if random.random() < 0.5:
        a_model, b_model = b_model, a_model

    pairs.append({
        "pair_id": qid,
        "type": by_q[qid][a_model]["type"],
        "question": by_q[qid][a_model]["question"],
        "A_model": a_model,
        "A_answer": by_q[qid][a_model]["answer"],
        "B_model": b_model,
        "B_answer": by_q[qid][b_model]["answer"],
    })

with open("data/pairs.json", "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

# Count how often each model is shown first (should be roughly balanced)
from collections import Counter
print("Total pairs:", len(pairs))
print(Counter(p["A_model"] for p in pairs))