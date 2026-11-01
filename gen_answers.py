import json
import time
import os
from llm import ask, ask_ollama

QUESTIONS_FILE = "data/questions.json"
OUTPUT_FILE = "data/answers.jsonl"

# A short instruction so both models answer in the same style.
# We do NOT say "be brief" or "be long": natural length matters
# later for the length-bias test.
SYSTEM = "You are a helpful Python expert. Answer the question."


def load_done():
    """Return the set of (question_id, model) pairs already saved,
    so we can resume after a crash without re-asking."""
    done = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                done.add((row["id"], row["model"]))
    return done


def main():
    # Load the 30 questions
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    done = load_done()

    # Two answerers: name stored in the file -> function that gets the answer
    models = {
        "llama-3.2-3b": lambda q: ask_ollama(f"{SYSTEM}\n\n{q}"),
        "gpt-oss-120b": lambda q: ask("groq", q, system=SYSTEM),
    }

    # "a" = append mode: each answer is written to disk immediately
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for q in questions:
            for model_name, get_answer in models.items():

                # Skip anything we already have
                if (q["id"], model_name) in done:
                    continue

                print(f"{q['id']} | {model_name} ...")
                try:
                    answer = get_answer(q["question"])
                except Exception as e:
                    # Don't crash the whole run; skip it and keep going.
                    # Rerunning the script later fills in anything missing.
                    print(f"  FAILED ({str(e)[:80]}), skipping for now")
                    continue

                # One JSON object per line = JSONL
                row = {
                    "id": q["id"],
                    "type": q["type"],
                    "question": q["question"],
                    "model": model_name,
                    "answer": answer,
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()   # force-save to disk now

                time.sleep(2)  # be gentle with free-tier rate limits

    print("Done.")


if __name__ == "__main__":
    main()