# Acceptance criteria - TakeMeter

Fill in these five entries yourself before training. Each needs your own
wording, a numeric target, and a reason tied to this question/statement dataset.
Cover at least three of the areas below. These prompts are a worksheet, not
completed acceptance criteria.

## 1.

**My criterion and numeric target:**

**Why I chose this target:**

## 2.

**My criterion and numeric target:**

**Why I chose this target:**

## 3.

**My criterion and numeric target:**

**Why I chose this target:**

## 4.

**My criterion and numeric target:**

**Why I chose this target:**

## 5.

**My criterion and numeric target:**

**Why I chose this target:**

---

Areas to think about:

- Overall accuracy: how often should held-out predictions be correct?
- Per-label performance: what F1 would make each label useful?
- Balance: how many examples should each label have, and what maximum share?
- Consistency: how often should two people applying the definitions agree,
  and on which posts?
- Confidence: should the most confident third be more accurate than the
  least confident third, and by how much?

For each criterion, name the evaluation set or count being checked.
Two labels mean a uniform random guess has expected accuracy of 50%.
The next unit checks model targets across seeds 42, 7, and 2024.
Choose your targets before looking at training results, then commit this file.
Keep the original targets if they are missed next unit.
