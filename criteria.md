# Acceptance criteria - TakeMeter

These targets were drafted with AI assistance and committed before the first
training run. They cover overall accuracy, per-label performance, balance,
and confidence. They have not been represented as unaided student work.

## 1. Held-out accuracy is at least 0.75

For each seed (42, 7, and 2024 in Unit 6), `accuracy` in the saved results
must be at least **0.75** on that seed's untouched test split.

**Reason:** With two labels, 50% is the expected accuracy of uniform random
guessing. A 75% target also exceeds the dataset's allowed majority share of
70%, so always predicting the larger label cannot satisfy this target.

## 2. Question F1 is at least 0.65

For each seed, `per_label.question.f1` must be at least **0.65** on the
held-out test split.

**Reason:** Genuine questions are harder to separate from rhetorical questions
and are the smaller class in the initial annotations. F1 measures both missed
requests and statements incorrectly treated as requests; 0.65 allows some
ambiguity without letting overall accuracy hide a weak question classifier.

## 3. Statement F1 is at least 0.75

For each seed, `per_label.statement.f1` must be at least **0.75** on the
held-out test split.

**Reason:** Statements have more examples and include many clear explanations
and personal accounts. They should score higher than questions, while the
quoted and self-answered questions still make this more than a punctuation task.

## 4. The final dataset has at least 200 unique posts and no label above 70%

The unsplit `labels.csv` must contain at least **200** nonempty, unique texts.
Every row must have exactly one of the two defined labels, and each label's
count divided by the total row count must be **at most 0.70**.

**Reason:** The original punctuation buckets contain rhetorical and quoted
questions, so equal bucket sizes do not imply equal label counts. Checking
actual labels prevents the statement class from overwhelming the training set;
checking exact text uniqueness prevents duplicate posts leaking between splits.

## 5. Confidence separates easier and harder predictions by at least 0.10

For each seed, subtract `confidence.accuracy_least_confident_third` from
`confidence.accuracy_most_confident_third` in its saved test results.
The difference must be at least **0.10** (10 percentage points).

**Reason:** A score that cannot distinguish easy requests from ambiguous
rhetorical comments is less useful for deciding which predictions need review.
A 10-point gap asks for a meaningful separation while acknowledging that this
small test set makes confidence estimates noisy.

---

Unit 5 records the first run with seed 42. Unit 6 checks the same unchanged
model targets across all three seeds; one passing seed alone is insufficient.
These targets stay in place if missed. No human annotation-agreement claim is
made because an independent human labeling pass has not occurred.
