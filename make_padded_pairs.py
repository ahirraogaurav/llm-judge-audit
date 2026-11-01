import json
import random

pairs = json.load(open("data/pairs.json", encoding="utf-8"))
ab = {r["pair_id"]: r for r in
      (json.loads(l) for l in open("results/verdicts_groq_AB.jsonl", encoding="utf-8"))}

# Filler sentences that carry NO new information
FILLER = [
    "This is a really important concept to understand carefully.",
    "Let me walk through this step by step so that everything is clear.",
    "It is worth thinking about this question from several angles.",
    "To recap what was just said, the points above are the main idea.",
    "Understanding this topic well will help you write better Python.",
    "I hope this explanation is helpful and easy to follow.",
    "Feel free to ask if you would like me to go into more detail.",
]

def pad(answer, question):
    """Add an intro that restates the question and filler lines,
    until the answer is about 1.5x its original length."""
    intro = f"Great question! You asked: \"{question.splitlines()[0]}\" Let me answer that.\n\n"
    target = int(len(answer) * 1.5)
    text = intro + answer + "\n\n"
    i = 0
    while len(text) < target:
        text += FILLER[i % len(FILLER)] + " "
        i += 1
    return text.strip()

# Candidates: pairs where the judge picked the big model and Llama lost
candidates = [p for p in pairs if ab[p["pair_id"]]["winner_model"] == "gpt-oss-120b"]
random.seed(42)
chosen = random.sample(candidates, 10)

padded = []
for p in chosen:
    p = dict(p)
    # Pad only the Llama answer, wherever it sits (A or B)
    if p["A_model"] == "llama-3.2-3b":
        p["A_answer"] = pad(p["A_answer"], p["question"])
    else:
        p["B_answer"] = pad(p["B_answer"], p["question"])
    padded.append(p)

json.dump(padded, open("data/pairs_padded.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("Padded pairs:", [p["pair_id"] for p in padded])