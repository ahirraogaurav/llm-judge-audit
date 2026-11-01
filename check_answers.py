import json
from collections import Counter

rows = [json.loads(l) for l in open("data/answers.jsonl", encoding="utf-8")]
print("Total rows:", len(rows))                      # should be 60
print(Counter(r["model"] for r in rows))             # 30 each

# Empty or very short answers usually mean an error
for r in rows:
    if len(r["answer"].strip()) < 20:
        print("Suspicious:", r["id"], r["model"], repr(r["answer"]))

# Average answer length per model (useful for the length-bias section)
for m in ["llama-3.2-3b", "gpt-oss-120b"]:
    lens = [len(r["answer"]) for r in rows if r["model"] == m]
    print(m, "avg chars:", sum(lens) // len(lens))