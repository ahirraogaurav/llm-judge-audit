# Can You Trust an LLM Judge? An Audit of Agreement and Bias

An experiment that measures how often an LLM judge agrees with a human grader on Python answers, and tests the judge for three known biases: **position bias**, **length bias** and **self-preference** (Zheng et al., 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*).

I graded 30 answer pairs myself, blind to which model wrote which, then compared my grades with two LLM judges and tried three mitigations.

> **Headline:** The judge agreed with me on **13/30** pairs (Cohen's κ ≈ 0). Swapping answer order changed **2** verdicts. Judging in both orders did **not** raise agreement (12/30). The judge mainly preferred the larger model's answer regardless of order, length note or judge family.

---

## Table of contents
1. [Why this project](#why-this-project)
2. [How it works](#how-it-works)
3. [Models and roles](#models-and-roles)
4. [Project structure](#project-structure)
5. [Setup](#setup)
6. [How to run it](#how-to-run-it)
7. [Results](#results)
8. [Two real flipped verdicts](#two-real-flipped-verdicts)
9. [What I found](#what-i-found)
10. [Limitations](#limitations)
11. [Takeaways](#takeaways)
12. [Future work](#future-work)

---

## Why this project

Teams use LLM judges to grade model outputs because it is cheap and fast: grading thousands of answers by hand is not realistic. But a judge is only useful if its verdicts match what humans would decide, and LLM judges have documented biases. This project checks one judge against my own grades and measures those biases directly instead of assuming they are absent.

---

## How it works

```
questions.json (30 Python questions)
        │
        ▼
 gen_answers.py ──► answers.jsonl (60 answers: Llama 3.2 3B + gpt-oss-120b)
        │
        ▼
 make_pairs.py ───► pairs.json (30 pairs, random A/B placement)
        │
        ├──────────────► grade.py ──► human.json   (my blind grades)
        │
        ▼
   judge.py  ───────► verdicts_*.jsonl  (judge verdicts: JSON, temperature 0)
        │
        ▼
 analyze.py / position_bias.py / length_bias.py /
 self_preference.py / analyze_fixes.py / length_check.py
        │
        ▼
   agreement, kappa, flip counts, bias results
```

**1. Questions and answers.** 30 Python questions (10 conceptual, 10 debugging, 10 write-a-function). Each is answered by a small local model and a larger cloud model. Answers are saved as JSONL (`id`, `type`, `question`, `model`, `answer`).

**2. Pairs.** The two answers to each question form a pair. Which model appears as "Answer A" is randomized (fixed seed), so the large model is not always shown first.

**3. Rubric.** One rubric (`rubric.md`) is shared by me and the judge: **correct > complete > clear**, with a weak, OK and strong example. It explicitly says length is not quality.

**4. Human grading.** `grade.py` shows each pair as "Answer A / Answer B" with model names hidden and saves my pick. I graded all 30 pairs before looking at any judge verdict. For code questions I ran the code.

**5. Judge.** `judge.py` gives the judge the rubric, the question and both answers, and asks for JSON only: `{"winner": "A" or "B", "reason": "..."}`. Temperature is 0. The script handles malformed JSON (retry once), saves each verdict as it goes, and resumes after a crash or rate limit. Verdicts record both the position the judge picked and the **real model** that won, so results stay comparable across orders.

**6. Metrics.**
- **Agreement:** pairs where the judge and I picked the same winner (X/30).
- **Cohen's kappa:** agreement corrected for chance. A judge that always picks the stronger model can score high raw agreement with a near-zero kappa.
- **Position bias:** re-run with answer order swapped; count verdicts that flipped only because of order.
- **Length bias:** pad the *losing* answer with content-free filler (restating the question, generic sentences) to about 1.5x its length, re-judge, and count verdicts that moved.
- **Self-preference:** compare how often the judge picks its own model's answers with how often I do, then check whether a judge from a different family behaves the same.

**7. Fixes tested.**
- **A:** judge each pair in both orders and count a win only if it holds both ways.
- **B:** add "answer length does not matter" to the judge prompt.
- **C:** use a judge from a different model family than the answerers.

---

## Models and roles

| Role | Model | Family | Where it runs |
|---|---|---|---|
| Small answerer | Llama 3.2 3B | Meta | Local (Ollama) |
| Large answerer | gpt-oss-120b | OpenAI-style | Groq free tier |
| Main judge | gpt-oss-120b | OpenAI-style | Groq free tier |
| Different-family judge | Qwen 2.5 7B | Alibaba | Local (Ollama) |

All models were used at temperature 0 and cost nothing to run. The judge doubles as one of the answerers on purpose, which is what makes the self-preference test possible.

---

## Project structure

```
.
├── README.md
├── requirements.txt
├── rubric.md                   # shared grading rubric
├── llm.py                      # one helper per provider (Groq API, Ollama), with retries
├── gen_answers.py              # collect answers from both models -> data/answers.jsonl
├── make_pairs.py               # build 30 answer pairs with randomized A/B placement
├── grade.py                    # blind human grading tool -> data/human.json
├── judge.py                    # run a judge (any provider, either order, optional length note)
├── analyze.py                  # agreement, kappa, by-type breakdown
├── position_bias.py            # count flips when order is swapped
├── show_flips.py               # print flipped verdicts with the judge's reasons
├── make_padded_pairs.py        # build 10 padded pairs for the length test
├── length_bias.py              # count verdicts moved by padding
├── self_preference.py          # judge-picks-own-answer vs human picks
├── analyze_fixes.py            # compare baseline and all fixes
├── length_check.py             # does the judge's choice track length ratio?
├── check_questions.py          # sanity checks for data files
├── check_answers.py
├── clean_answers.py
├── data/
│   ├── questions.json
│   ├── answers.jsonl
│   ├── pairs.json
│   ├── pairs_padded.json
│   └── human.json              # my blind grades
└── results/
    └── verdicts_*.jsonl        # every judge run
```

---

## Setup

**Requirements:** Python 3.10+, [Ollama](https://ollama.com), and a free [Groq](https://console.groq.com) API key.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Mac/Linux

# 2. Install libraries
pip install -r requirements.txt

# 3. Pull the local models
ollama pull llama3.2:3b
ollama pull qwen2.5:7b

# 4. Add your key to a .env file in the project root (never commit this file)
#    GROQ_API_KEY=your_key_here
```

Free-tier limits change often. If a model name or limit differs for your account, update the `PROVIDERS` table in `llm.py`.

---

## How to run it

Run the scripts in this order:

```bash
python gen_answers.py            # 1. collect answers (resumable)
python make_pairs.py             # 2. build pairs
python grade.py                  # 3. grade all 30 pairs yourself, BEFORE viewing verdicts
python judge.py --judge groq --order AB --out results/verdicts_groq_AB.jsonl
python analyze.py                # 4. agreement + kappa

# Bias tests
python judge.py --judge groq --order BA --out results/verdicts_groq_BA.jsonl
python position_bias.py          # position bias
python make_padded_pairs.py
python judge.py --judge groq --order AB --pairs data/pairs_padded.json --out results/verdicts_padded_AB.jsonl
python length_bias.py            # length bias
python self_preference.py        # self-preference

# Fixes
python judge.py --judge groq --order AB --length-note --out results/verdicts_groq_AB_note.jsonl
python judge.py --judge "ollama:qwen2.5:7b" --order AB --out results/verdicts_qwen_AB.jsonl
python judge.py --judge "ollama:qwen2.5:7b" --order BA --out results/verdicts_qwen_BA.jsonl
python analyze_fixes.py          # compare everything
python length_check.py           # length ratio vs judge picks
```

Every script that calls a model saves results as it goes and skips finished pairs, so you can stop and rerun after a rate limit without losing work. Group-level numbers depend on your own grades in `data/human.json`.

---

## Results

### Setup facts
- 30 questions: 10 conceptual, 10 debugging, 10 code.
- gpt-oss-120b answers averaged **3,724 characters**, versus **1,292** for Llama (about 2.9x longer).
- I picked gpt-oss-120b's answer in **13/30** pairs and Llama's in **17/30**.

### Agreement before and after fixes

| Judge setup | Agreement with me | Pairs decided | Cohen's κ |
|---|---|---|---|
| Baseline: gpt-oss judge, one order | **13/30** | 30/30 | -0.02 |
| Fix A: judged in both orders | 12/30 | 28/30 | 0.00 |
| Fix B: "length doesn't matter" note | 13/30 | 30/30 | 0.00 |
| Fix C: different-family judge (Qwen) | 15/30 | 30/30 | 0.10 |
| Fix C + A: Qwen, both orders | 12/30 | 27/30 | 0.00 |

Pairs with no stable winner (a tie after both orders) count as disagreement. Baseline agreement by question type: conceptual 3/10, debugging 6/10, code 4/10.

### Bias tests

| Test | Result |
|---|---|
| Position bias (gpt-oss judge) | **2/30** verdicts flipped when order was swapped |
| Position bias (Qwen judge) | 3/30 flipped |
| Length bias (filler padding on 10 losing answers) | **0/10** verdicts moved |
| Length-neutral prompt note | Judge picked the large model 28/30 → **30/30** |
| Self-preference | Judge picked its own model's answer **28/30**; I picked it 13/30 |
| Self-preference, pairs where I preferred Llama | Judge still picked its own answer in 16/17 |
| Cross-family control | Qwen also picked gpt-oss in **28/30** |

### Does the judge's choice track length?

Pairs split into thirds by how much longer gpt-oss's answer was:

| Group | Avg length ratio | Judge picks big model | I pick big model |
|---|---|---|---|
| Shortest ratio | 1.9x | 10/10 | 6/10 |
| Middle | 2.6x | 10/10 | 3/10 |
| Longest ratio | 9.1x | 8/10 | 4/10 |

A bigger length gap did not make the judge pick the longer answer more often.

---

## Two real flipped verdicts

**q21: `is_palindrome(s)`.** In the original order the judge picked Llama, calling the other answer's ASCII-only regex "less technically accurate". With the order swapped it picked gpt-oss, saying both were correct but one was "more complete", with documentation, examples and a test harness.

**q30: timing decorator.** In the original order the judge picked Llama as "clearer and more concise". With the order swapped it picked gpt-oss, citing a fully correct decorator with `perf_counter`, a `finally` block and metadata preservation. Both flips happened on near-ties where the judge called both answers correct and favored whichever sat in slot A.

---

## What I found

1. **The judge mostly picks the larger model, whatever the setup.** Its agreement with me equals roughly how often I picked that model (13/30), and kappa is about 0. The raw agreement number reflects a base rate, not judging skill.
2. **None of the three fixes raised agreement.** Position bias was small, so judging in both orders mostly turned a few pairs into ties. The length-neutral note made the judge pick the large model *more* (30/30).
3. **Self-preference is not the main cause.** A judge from a different family with no stake in the answers also picked gpt-oss 28/30.
4. **Length alone does not explain the preference.** Filler padding did not move any verdicts (0/10), and the judge's picks did not rise with the length ratio. The judge's written reasons repeatedly praise "more complete" answers with documentation, tests and options, which suggests it rewards extra substance. My own grading, following "correct first, clear second", often preferred the more direct answer. With 10 pairs per group I cannot separate richness from plain quality.

---

## Limitations

- **Small sample:** 30 pairs and one human grader. My grades are not ground truth, and the judges may weigh "complete" more heavily than I did.
- **Imperfect blinding:** model names were hidden, but answer length hints at which model wrote what.
- **Length test:** only 10 pairs, one padding style, and a single 1.5x padding level.
- **Judge strength confound:** Qwen 2.5 7B is a much smaller judge than gpt-oss-120b, so "different family" and "weaker judge" are mixed together.
- **Provider changes:** I originally planned Gemini as the large answerer, but free-tier 503 and 429 errors led me to use gpt-oss-120b. Mistral and Gemini were also rate-limited when I tried them as judges.
- **Free-tier limits:** token caps changed how I spread runs across days. They did not affect results because every run saved its progress.

---

## Takeaways

- **Why teams use LLM judges:** cost and speed. A judge can grade thousands of outputs, which a human cannot.
- **Why still check against human grades:** this judge produced confident, well-written reasons while its agreement with me was no better than chance (κ ≈ 0). Without a human baseline I would not have noticed.
- **Which fix helped most:** none did, and that is the result. Fixes for the documented biases do not help when the real disagreement is about what counts as a better answer. A tighter rubric, for example penalizing unrequested extras, is the more promising next fix.
- **Report kappa, not just agreement.** A judge that always picks the stronger model can look decent on raw agreement.

---

## Future work

- Rewrite the rubric to penalize unrequested extras, then re-measure.
- Add a second human grader to measure my own consistency.
- Test a stronger cross-family judge (for example Gemini or Mistral) to separate "different family" from "weaker judge".
- Scale beyond 30 pairs, with more padding levels and padding types.
- Compare against reference-based checks for the code questions (run unit tests instead of relying on opinion).

---

## Reference

Zheng, L., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS Datasets and Benchmarks.
