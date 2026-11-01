import json

path = "data/answers.jsonl"
rows = [json.loads(l) for l in open(path, encoding="utf-8")]

# Keep only the two models we are using now
keep = [r for r in rows if r["model"] in ("llama-3.2-3b", "gpt-oss-120b")]
print(f"Kept {len(keep)} of {len(rows)} rows")

with open(path, "w", encoding="utf-8") as f:
    for r in keep:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")