import json

def load(path):
    return {r["pair_id"]: r for r in
            (json.loads(l) for l in open(path, encoding="utf-8"))}

before = load("results/verdicts_groq_AB.jsonl")
after = load("results/verdicts_padded_AB.jsonl")

# A pair "scored higher" if padded Llama now wins but lost before
moved = [i for i in after
         if before[i]["winner_model"] == "gpt-oss-120b"
         and after[i]["winner_model"] == "llama-3.2-3b"]
print(f"Padding flipped the verdict to the padded answer: {len(moved)}/{len(after)}")
print("Pairs:", moved)