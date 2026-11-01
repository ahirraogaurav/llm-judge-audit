# Grading rubric

You are comparing two answers (A and B) to a Python question.
Decide which answer is better overall using three criteria,
in this order of importance:

1. **Correct**: Is everything stated technically accurate? Does any
   code actually work? A wrong claim or broken code is a serious flaw.
2. **Complete**: Does it answer every part of the question
   (e.g. "why" AND "how to fix")? Does it include what a learner
   needs to understand?
3. **Clear**: Is it easy to follow, well organized, and free of
   unnecessary text?

## Rules
- Correctness beats everything. A shorter correct answer beats a longer
  answer with an error.
- **Length is NOT quality.** Do not prefer an answer because it is
  longer, has more formatting, or sounds more confident.
- Extra detail only counts if it is accurate and useful to the question.
- Repeating the question, filler, or restating the same point adds
  nothing.
- Pick the better answer even if both are good or both are weak.
  If truly equal, pick the one that is more correct, then more clear.

## Example: "What is a mutable default argument, and why can
`def f(x, items=[])` cause bugs?"

**Weak:** "A mutable default is a default value that can change.
It can cause bugs because the list changes."
(Vague, never explains that the list is created once and shared
between calls.)

**OK:** "The default list `[]` is created once when the function is
defined, not each call, so every call that doesn't pass `items` shares
the same list and appends accumulate."
(Correct and explains the cause, but gives no fix and no example.)

**Strong:** The OK answer, plus a short demo showing the bug
(`f(1)` then `f(2)` returning `[1, 2]`) and the standard fix:
`def f(x, items=None): if items is None: items = []`.
(Correct, complete, clear.)