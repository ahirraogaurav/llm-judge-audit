import argparse
import json
import os
import re
import time
from llm import ask

# The same rubric you will use yourself
RUBRIC = open("rubric.md", encoding="utf-8").read()

# Judge prompt. __PLACEHOLDERS__ get replaced below (we avoid str.format
# because the JSON braces in the prompt would confuse it).
TEMPLATE = """You are an impartial judge of Python answers.

__RUBRIC__

__EXTRA__
Question:
__QUESTION__

Answer A:
__ANSWER_A__

Answer B:
__ANSWER_B__

Which answer is better according to the rubric?
Reply with JSON only, no other text, in exactly this format:
{"winner": "A" or "B", "reason": "<one or two sentences>"}"""

# Optional instruction used later for the length-bias fix (Day 3)
LENGTH_NOTE = ("Important: answer length does not matter. Do not prefer an "
               "answer because it is longer or has more formatting.\n")


def parse_verdict(text):
    """Pull the JSON object out of the model's reply.
    Models sometimes wrap JSON in code fences or add extra text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if data.get("winner") in ("A", "B"):
        return data
    return None


def judge_pair(provider, pair, order, extra=""):
    """Judge one pair. order 'AB' shows A first; 'BA' swaps the positions.
    Returns (winner_model, shown_winner, reason)."""

    # Decide which real answer is shown in position 1 and position 2
    if order == "AB":
        first = (pair["A_model"], pair["A_answer"])
        second = (pair["B_model"], pair["B_answer"])
    else:
        first = (pair["B_model"], pair["B_answer"])
        second = (pair["A_model"], pair["A_answer"])

    prompt = (TEMPLATE
              .replace("__RUBRIC__", RUBRIC)
              .replace("__EXTRA__", extra)
              .replace("__QUESTION__", pair["question"])
              .replace("__ANSWER_A__", first[1])
              .replace("__ANSWER_B__", second[1]))

    # Try up to 2 times in case the JSON comes back malformed
    for _ in range(2):
        reply = ask(provider, prompt)
        verdict = parse_verdict(reply)
        if verdict:
            shown = verdict["winner"]                   # "A" or "B" as the judge saw it
            winner_model = first[0] if shown == "A" else second[0]
            return winner_model, shown, verdict.get("reason", "")
    return None, None, "PARSE_FAILED"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--judge", default="groq")        # provider name from llm.py
    p.add_argument("--order", default="AB", choices=["AB", "BA"])
    p.add_argument("--pairs", default="data/pairs.json")
    p.add_argument("--out", required=True)           # where to save verdicts
    p.add_argument("--length-note", action="store_true")
    args = p.parse_args()

    pairs = json.load(open(args.pairs, encoding="utf-8"))

    # Resume support: skip pairs already saved in the output file
    done = set()
    if os.path.exists(args.out):
        for line in open(args.out, encoding="utf-8"):
            done.add(json.loads(line)["pair_id"])

    extra = LENGTH_NOTE if args.length_note else ""

    with open(args.out, "a", encoding="utf-8") as out:
        for pair in pairs:
            if pair["pair_id"] in done:
                continue
            print(f"judging {pair['pair_id']} ({args.order}) ...")
            try:
                winner, shown, reason = judge_pair(args.judge, pair, args.order, extra)
            except Exception as e:
                print(f"  FAILED ({str(e)[:80]}), will retry on next run")
                continue

            row = {
                "pair_id": pair["pair_id"],
                "judge": args.judge,
                "order": args.order,
                "winner_model": winner,     # the real model that won
                "shown_winner": shown,      # "A"/"B" position the judge picked
                "reason": reason,
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            time.sleep(2)                   # stay under the rate limit

    # Print only counts, NOT the winners, so you stay unbiased
    rows = [json.loads(l) for l in open(args.out, encoding="utf-8")]
    failed = sum(1 for r in rows if r["winner_model"] is None)
    print(f"Saved {len(rows)} verdicts, {failed} parse failures.")


if __name__ == "__main__":
    main()