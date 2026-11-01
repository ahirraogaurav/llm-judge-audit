import json
from collections import Counter

def load(path):
    return {r["pair_id"]: r for r in
            (json.loads(l) for l in open(path, encoding="utf-8"))}

ab = load("results/verdicts_groq_AB.jsonl")   # original order
ba = load("results/verdicts_groq_BA.jsonl")   # swapped order

ids = sorted(set(ab) & set(ba))

# A flip = the judge picked a different real model after we only swapped positions
flips = [i for i in ids
         if ab[i]["winner_model"] and ba[i]["winner_model"]
         and ab[i]["winner_model"] != ba[i]["winner_model"]]
print(f"Flipped verdicts: {len(flips)}/{len(ids)}")
print("Flipped pairs:", flips)

# Which position does the judge favor in each run?
print("\nShown winner, AB run:", dict(Counter(ab[i]["shown_winner"] for i in ids)))
print("Shown winner, BA run:", dict(Counter(ba[i]["shown_winner"] for i in ids)))