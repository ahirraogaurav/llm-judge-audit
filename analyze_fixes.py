import json
import math
from sklearn.metrics import cohen_kappa_score

# Your grades: {pair_id: {"pick": "A"/"B", "winner_model": ...}}
human = json.load(open("data/human.json", encoding="utf-8"))

BIG = "gpt-oss-120b"   # the big model (also the baseline judge)


def load(path):
    """Read a verdicts file -> {pair_id: winner model (or None if parsing failed)}."""
    return {r["pair_id"]: r["winner_model"] for r in
            (json.loads(l) for l in open(path, encoding="utf-8"))}


def both_orders(ab, ba):
    """Fix A: a win only counts if the same real model wins in BOTH orders.
    Otherwise the pair becomes None (no stable winner = a tie)."""
    return {i: (ab[i] if ab.get(i) and ab.get(i) == ba.get(i) else None)
            for i in ab}


def report(name, verdict):
    """Print agreement with you for one set of verdicts."""
    ids = sorted(human)

    # Agreement: same winner as you. A tie (None) counts as NOT agreeing.
    agree = sum(verdict.get(i) == human[i]["winner_model"] for i in ids)

    # Pairs where the judge produced a stable winner
    decided = [i for i in ids if verdict.get(i)]

    # Kappa only on decided pairs (it needs a real label from both sides)
    kappa = "n/a"
    if len(decided) > 1:
        h = [human[i]["winner_model"] for i in decided]
        j = [verdict[i] for i in decided]
        k = cohen_kappa_score(h, j)
        if not math.isnan(k):   # nan happens if one side picked a single model every time
            kappa = f"{k:.2f}"

    print(f"{name:<40} agree {agree:>2}/30 | decided {len(decided):>2}/30 | kappa {kappa}")


def picks_big(verdict):
    """How many pairs the judge gave to the big model."""
    return sum(v == BIG for v in verdict.values())


# ---------------- Baseline and Fix A (uses files you already have) ----------------
print("--- Baseline and fixes ---")
groq_ab = load("results/verdicts_groq_AB.jsonl")
groq_ba = load("results/verdicts_groq_BA.jsonl")

report("Baseline: groq, one order", groq_ab)
report("Fix A: groq, both orders", both_orders(groq_ab, groq_ba))

# ---------------- Fix B: length-neutral instruction ----------------
try:
    note = load("results/verdicts_groq_AB_note.jsonl")
    report("Fix B: groq + length note", note)
    print(f"   groq picks big model: {picks_big(groq_ab)}/30 -> {picks_big(note)}/30 with note")
except FileNotFoundError:
    print("Fix B: not run yet")

# ---------------- Fix C: different-family judge (Qwen via Ollama) ----------------
try:
    q_ab = load("results/verdicts_qwen_AB.jsonl")
    q_ba = load("results/verdicts_qwen_BA.jsonl")

    report("Fix C: qwen (other family), one order", q_ab)
    report("Fix C + A: qwen, both orders", both_orders(q_ab, q_ba))

    # Position flips for Qwen: same pair, different winner after swapping order
    flips = sum(1 for i in q_ab if q_ab[i] != q_ba.get(i))
    print(f"   Qwen position flips: {flips}/30")

    # The key self-preference check: does a non-gpt-oss judge also prefer gpt-oss?
    print(f"   Qwen picks big model: {picks_big(q_ab)}/30 (groq judge: {picks_big(groq_ab)}/30, you: "
          f"{sum(h['winner_model'] == BIG for h in human.values())}/30)")
except FileNotFoundError:
    print("Fix C: not run yet")

# ---------------- Reference: how you picked ----------------
print("\nYou picked the big model:",
      sum(h["winner_model"] == BIG for h in human.values()), "/ 30")