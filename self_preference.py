import json

human = json.load(open("data/human.json", encoding="utf-8"))
judge = {r["pair_id"]: r["winner_model"] for r in
         (json.loads(l) for l in open("results/verdicts_groq_AB.jsonl", encoding="utf-8"))}

ids = sorted(set(human) & set(judge))
OWN = "gpt-oss-120b"   # the judge's own answers

# How often does the judge pick its own answer vs how often YOU pick it
judge_own = sum(judge[i] == OWN for i in ids)
human_own = sum(human[i]["winner_model"] == OWN for i in ids)
print(f"Judge picks its own answer: {judge_own}/{len(ids)}")
print(f"You pick that model's answer: {human_own}/{len(ids)}")

# Where you preferred the OTHER model, how often did the judge still pick its own?
you_other = [i for i in ids if human[i]["winner_model"] != OWN]
judge_own_there = sum(judge[i] == OWN for i in you_other)
print(f"\nPairs where you preferred Llama: {len(you_other)}")
print(f"Judge still picked its own answer in: {judge_own_there}/{len(you_other)}")