import json
from collections import Counter
from sklearn.metrics import cohen_kappa_score

# Your grades: {pair_id: {"pick": "A"/"B", "winner_model": ...}}
human = json.load(open("data/human.json", encoding="utf-8"))

# Judge verdicts: one JSON object per line
verdicts = [json.loads(l) for l in
            open("results/verdicts_groq_AB.jsonl", encoding="utf-8")]
judge = {v["pair_id"]: v["winner_model"] for v in verdicts}

# Pair types (conceptual / debugging / code) for the breakdown below
pairs = json.load(open("data/pairs.json", encoding="utf-8"))
ptype = {p["pair_id"]: p["type"] for p in pairs}

# Keep only pairs that both you and the judge have a result for
ids = sorted(set(human) & {k for k, v in judge.items() if v})
h = [human[i]["winner_model"] for i in ids]   # your winner per pair
j = [judge[i] for i in ids]                   # judge's winner per pair

# 1) Raw agreement: how many pairs have the same winner
agree = sum(a == b for a, b in zip(h, j))
print(f"Agreement: {agree}/{len(ids)}")

# 2) Cohen's kappa: agreement corrected for chance (1 = perfect, 0 = chance)
print(f"Cohen's kappa: {cohen_kappa_score(h, j):.2f}")

# 3) How often each side picks each model (reveals lopsided picking)
print("\nYou picked:  ", dict(Counter(h)))
print("Judge picked:", dict(Counter(j)))

# 4) Agreement by question type
print("\nBy type:")
for t in ["conceptual", "debugging", "code"]:
    t_ids = [i for i in ids if ptype[i] == t]
    t_agree = sum(human[i]["winner_model"] == judge[i] for i in t_ids)
    print(f"  {t}: {t_agree}/{len(t_ids)}")

# 5) The pairs you disagreed on (look at these later)
print("\nDisagreements:", [i for i in ids if human[i]["winner_model"] != judge[i]])
