import json

pairs = {p["pair_id"]: p for p in json.load(open("data/pairs.json", encoding="utf-8"))}

def load(path):
    return {r["pair_id"]: r for r in
            (json.loads(l) for l in open(path, encoding="utf-8"))}

ab = load("results/verdicts_groq_AB.jsonl")
ba = load("results/verdicts_groq_BA.jsonl")

for i in ["q21", "q30"]:
    print("=" * 60)
    print(i, pairs[i]["question"])
    print("Original order  ->", ab[i]["winner_model"], "|", ab[i]["reason"])
    print("Swapped order   ->", ba[i]["winner_model"], "|", ba[i]["reason"])