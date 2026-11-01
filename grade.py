import json
import os

PAIRS_FILE = "data/pairs.json"
OUT_FILE = "data/human.json"

pairs = json.load(open(PAIRS_FILE, encoding="utf-8"))

# Load grades already saved, so you can stop and resume any time
grades = {}
if os.path.exists(OUT_FILE):
    grades = json.load(open(OUT_FILE, encoding="utf-8"))

todo = [p for p in pairs if p["pair_id"] not in grades]
print(f"{len(grades)} graded, {len(todo)} to go. Type A or B, or q to quit.\n")

for i, p in enumerate(todo, 1):
    # Model names are NOT printed: you only see "Answer A" and "Answer B"
    print("=" * 70)
    print(f"[{p['pair_id']}]  ({len(grades) + 1} of {len(pairs)})")
    print("QUESTION:\n" + p["question"])
    print("-" * 70)
    print("ANSWER A:\n" + p["A_answer"])
    print("-" * 70)
    print("ANSWER B:\n" + p["B_answer"])
    print("=" * 70)

    while True:
        pick = input("Better answer (A/B, q to quit): ").strip().upper()
        if pick in ("A", "B", "Q"):
            break
        print("Please type A, B or q.")

    if pick == "Q":
        break

    # Save the position you picked, plus the real model behind it
    grades[p["pair_id"]] = {
        "pick": pick,
        "winner_model": p["A_model"] if pick == "A" else p["B_model"],
    }
    json.dump(grades, open(OUT_FILE, "w", encoding="utf-8"), indent=2)

print(f"\nSaved. {len(grades)} of {len(pairs)} graded.")