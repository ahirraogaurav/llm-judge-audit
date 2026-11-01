import json

pairs = {p["pair_id"]: p for p in json.load(open("data/pairs.json", encoding="utf-8"))}
human = json.load(open("data/human.json", encoding="utf-8"))
judge = {r["pair_id"]: r["winner_model"] for r in
         (json.loads(l) for l in open("results/verdicts_groq_AB.jsonl", encoding="utf-8"))}

BIG, SMALL = "gpt-oss-120b", "llama-3.2-3b"

def lengths(p):
    """Return (big answer length, small answer length) in characters."""
    a, b = len(p["A_answer"]), len(p["B_answer"])
    return (a, b) if p["A_model"] == BIG else (b, a)

# Sort pairs by how much longer the big model's answer is
rows = []
for i, p in pairs.items():
    big, small = lengths(p)
    rows.append((i, big / small))
rows.sort(key=lambda r: r[1])

# Split into thirds: big answer only slightly longer / medium / much longer
n = len(rows) // 3
groups = {"shortest ratio": rows[:n], "middle": rows[n:2*n], "longest ratio": rows[2*n:]}

print(f"{'group':<16}{'avg ratio':>10}{'judge picks big':>18}{'you pick big':>15}")
for name, g in groups.items():
    ids = [i for i, _ in g]
    avg = sum(r for _, r in g) / len(g)
    j = sum(judge[i] == BIG for i in ids)
    h = sum(human[i]["winner_model"] == BIG for i in ids)
    print(f"{name:<16}{avg:>10.1f}{f'{j}/{len(ids)}':>18}{f'{h}/{len(ids)}':>15}")