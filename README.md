# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

TakeMeter will sort public Hacker News comments into `question` and `statement`.
It measures whether the author asks for information, not whether the comment is
correct or high quality. This is the Unit 5 build only; no stretch features.

The labeled dataset contains 255 whole comments. Five numeric targets were
committed before training. I directed the project and used AI to accelerate implementation and testing;
the workflow is described below.

## Label Taxonomy

### `question`

**Definition:** The author's own words ask the reader for information, advice,
or clarification.

**Example 1:**

> Maybe a related question:
> How do you keep the IEC 62443-4-1 auditors happy?

[Source](https://news.ycombinator.com/item?id=50158503)

**Example 2:**

> Serious question - how do you even learn all of the skills to do something like this? Where would you start?

[Source](https://news.ycombinator.com/item?id=50158532)

### `statement`

**Definition:** The author's own words provide information, an opinion, an
answer, or a reaction without asking the reader for information.

**Example 1:**

> This has nothing to do with LLMs. The *BSDs have been porting Linux video drivers for years.

[Source](https://news.ycombinator.com/item?id=50158911)

**Example 2:**

> I wanted to learn more about photography, I started asking an LLM and it helped me immensively. Definitely not the same realm but if you wanna pick up new skills, LLMs have tons of beginner friendly ways to explain things!

[Source](https://news.ycombinator.com/item?id=50158700)

### The hardest boundary

**Which two labels:** `question` and `statement`, especially rhetorical or
quoted questions.

**Decision rule:** Ignore quoted text when deciding what the author is doing.
If their own words request information or clarification, use `question`, even
when most of the comment is an opinion. If a question only emphasizes a claim
or the author answers it themselves, use `statement`. A question mark alone is
not enough. A clear request without a question mark still counts as `question`.

**Three observed distinctions:** Some comments ask for
practical advice, some provide explanations or personal experience, and some
phrase disagreement as a rhetorical question. Two labels keep the task basic;
the boundary rule separates genuine requests from rhetorical statements.

**Boundary stress test (synthetic; excluded from the dataset):**

| Boundary example | Label | Rule |
|---|---|---|
| This fails on Windows. Does anyone know a fix? | question | Direct request. |
| Why pay for that? The free version does everything I need. | statement | Rhetorical claim. |
| You asked, "Does it work?" Yes, on Linux. | statement | Quoted question, own answer. |
| You asked, "Does it work?" Which version did you try? | question | Own clarification request. |
| I wonder if someone could explain the error message. | question | Clear request without a question mark. |
| I used to wonder why it failed; the logs explained it. | statement | Resolved personal account. |
| It looks useful, but where is the documentation? | question | Opinion plus information request. |
| Who needs another subscription? I am keeping the free tool. | statement | Rhetorical reaction. |

## The Dataset

**Source:** Public [Hacker News](https://news.ycombinator.com/) comments,
collected through the [Algolia HN API](https://hn.algolia.com/api).
`data/collected_posts.json` preserves each whole comment's rendered text,
source URL, and publication time. HTML formatting is removed; posts are not
shortened. Collection excludes comments under ten words and duplicate text.

**Sampling:** The initial 220 comments came from five API pages, shuffled with
seed 42: 20 unfiltered comments, 100 containing `?`, and 100 without it.
After semantic labeling showed too many statements, the collection was expanded
to ten cached pages and 35 additional genuine questions were included.
The final sample is deliberately selected and does not represent Hacker News's
natural label frequencies. Each retained comment has its own unique source URL.

**Labeling:** I used AI to assign semantic labels to the full comments.
Every note records `AI-labeled`, the source URL, and a reason. No row is marked
`cold`. `labels.csv` is the one unsplit dataset; the notebook creates the split.

**Counts per label:**

| Label | Count | Share |
|---|---:|---:|
| question | 81 | 31.76% |
| statement | 174 | 68.24% |
| **Total** | **255** | **100%** |

There are no empty texts, duplicate texts, duplicate source URLs, or undefined
labels. The largest label stays below 70%.

**Punctuation check:** 62 statements contain a question mark, while one question
requests others' thoughts without one. Punctuation alone therefore does not
define the labels. It is still correlated with them, and the selected sample
and small size limit how well results will generalize to unseen discussions.
Comments from related threads can also share wording; exact-text deduplication
does not eliminate that source of similarity.

**Three hard cases and the decisions used in the CSV:**

1. [Quoted question followed by an answer](https://news.ycombinator.com/item?id=50158399):
   the comment quotes a question about StarCraft assets and answers "Because
   it's cool." Could be question/statement. Chosen label: `statement`,
   because the author's own words are an answer.
2. [Self-answered purchasing question](https://news.ycombinator.com/item?id=50158645):
   the author asks why they would buy the RTX Spark, then explains why they
   prefer the DGX Spark. Could be question/statement. Chosen label:
   `statement`, because the question introduces the author's own conclusion.
3. [An opinion followed by a request](https://news.ycombinator.com/item?id=50158542):
   the author enjoyed a video but asks whether clipping was a camera bug.
   Could be question/statement. Chosen label: `question`, because the
   author requests clarification that the comment does not resolve.

## The Training Run

**Base model:** `distilbert-base-uncased`.

**Settings:** 3 epochs, learning rate `2e-5`, batch size 16, maximum length
128 tokens, seed 42. No training hyperparameters were changed.

**Device:** CPU, PyTorch `2.11.0+cpu`, with four CPU threads. This Windows run
loaded PyTorch before the notebook kernel libraries to avoid a DLL startup
error. All eight code cells in sections 1-5 completed without a cell error.
A console encoding error occurred only while replaying the saved outputs after
the notebook had finished; the notebook outputs, metrics, split, and saved
model were already written successfully.

**Split:** The starter's stratified 70/15/15 split produced the following
counts (rounding gives 177/39/39). Raw comments remain whole in the CSV;
the tokenizer truncates model inputs to 128 tokens.

| Label | Train | Validation | Test |
|---|---:|---:|---:|
| question | 57 | 12 | 12 |
| statement | 120 | 27 | 27 |
| **Total** | **177** | **39** | **39** |

Neither test label has fewer than eight examples. Test rows were not used for
training or validation; exact texts do not overlap between the three splits.

**Saved results:** `results.json` and `test_split.csv`. The executed notebook
also contains the training output. The trained weights and tokenizer are
saved locally in `models/takemeter/`, which the starter intentionally excludes
from Git because model files are large.

| Held-out measure | Result |
|---|---:|
| Accuracy | 0.6923 |
| Macro F1 | 0.4091 |
| Question F1 | 0.0000 |
| Statement F1 | 0.8182 |

The model predicted `statement` for every test row: 27 correct statements and
12 missed questions. The run is complete, but it did not learn a useful
question classifier. The first run is retained as evidence, and the criteria
have not been lowered to fit it. Unit 6 below records the repeated trials, baseline, and one measured improvement.

**Before training:** Criteria were committed in `0b7abed` and the final dataset
in `38f619e`, before the notebook generated the results.

## How I Used AI

I directed the project and used AI to speed up data preparation, coding,
experiment execution, and documentation.

1. For dataset preparation, I used AI to collect public comments, suggest the
   label boundary, generate the CSV annotations, and draft acceptance criteria
   before training. The eight synthetic boundary examples were kept out of the
   dataset, and semantic labeling led to collecting 35 additional questions.
2. For testing, I used AI to automate the baseline, six training trials,
   staff-taxonomy annotations, metric checks, and report drafting. The single
   learning-rate change was committed before the after trials, and the staff
   annotations were committed before opening the instructor's key.

**Annotation disclosure:** The 255 project labels and 30 staff-set annotations
were generated with AI. An unaided 20-post cold-labeling pass was not performed.
The agreement result measures those annotations against staff's labels.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

**Prediction committed before the baseline run (`9d385b3`):** I expected the trained model to retain higher statement recall and the baseline to recognize more genuine questions. This was informed by the already-known Unit 5 majority-class behavior, not a blind prediction before seeing those old results.

The local zero-shot model was `facebook/bart-large-mnli`, using the unchanged one-sentence definitions in `label_definitions.txt` and the starter's hypothesis template. Both columns score all **39 identical posts** in the original `test_split.csv`; no random-sample fallback or cap was used. No bare-label comparison or other stretch feature was added.

| Measure | Baseline | Trained (Unit 5, seed 42) | Trained - baseline |
|---|---:|---:|---:|
| Accuracy | 0.795 | 0.692 | -0.103 |
| Macro F1 | 0.783 | 0.409 | -0.374 |
| question F1 | 0.733 | 0.000 | -0.733 |
| statement F1 | 0.833 | 0.818 | -0.015 |

Baseline accuracy minus the original trained accuracy is +0.103. The original classifier's question recall is 0.000, versus 0.917 for the baseline. A useful comparison requires both the aggregate and the question score: high statement recall alone can be achieved by always choosing the majority class. This one baseline comparison applies to the original seed-42 posts, not to the other seeds' different test sets.

## Run Log — Before

Every seed started from the same pretrained model and used its own stratified 70/15/15 split: 177 training, 39 validation, and 39 test rows. The device was CPU with four threads and PyTorch `2.11.0+cpu`. Settings were 3 epochs, learning rate `2e-5`, batch size 16, and maximum length 128. The notebook's exact split/train/evaluate functions were run by `run_trials.py`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---:|---:|---:|---|
| 1. Overall accuracy | >=0.75 | 0.692 | 0.692 | 0.692 | MISSED |
| 2. Question F1 | >=0.65 | 0.000 | 0.000 | 0.000 | MISSED |
| 3. Statement F1 | >=0.75 | 0.818 | 0.818 | 0.818 | MET |
| 4. Dataset size/balance | >=200 unique; max share <=70% | 255; 68.24% max | 255; 68.24% max | 255; 68.24% max | MET |
| 5. Confidence gap | >=0.10 | 0.692 | 0.692 | 0.231 | MET |

Accuracy spread across seeds: **0.000** (0.0 percentage points). That is below ten points, but a stable majority-class predictor can still be consistently unhelpful.

Criterion 4 checks the unchanged whole dataset, so its identical entries are one shared structural check rather than three independent data collections. All numeric model targets must pass in every seed.

### Confusion matrix (before, seed 42)

| true \ predicted | question | statement |
|---|---:|---:|
| **question** | 0 | 12 |
| **statement** | 0 | 27 |

The largest off-diagonal cell is **12 true question comments predicted as statement**. The reverse direction has 0 errors. This names the direction of the failed boundary; it is not simply an overall error count. The other seeds' matrices are saved in the before JSON.

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict before improvement | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy | >=0.75 | MISSED | Minimum across seeds: 0.692. |
| 2 | Question F1 | >=0.65 | MISSED | Minimum across seeds: 0.000. |
| 3 | Statement F1 | >=0.75 | MET | Minimum across seeds: 0.818. |
| 4 | Dataset size/balance | >=200 unique; max <=70% | MET | 255 unique rows; largest share 68.24%. |
| 5 | Confidence gap | >=0.10 | MET | Minimum across seeds: 0.231. |

**Diagnosis of the misses:** The main failure is the question/statement boundary: question recall and F1 must be read alongside the off-diagonal question-to-statement counts. Statements make up 174/255 rows (68.24%), so they offer the optimizer an easy majority-class solution. Each test split still contains 12 questions and each training split contains 57 questions; the minority class is smaller, but this is not a zero-support or fewer-than-eight-test-examples failure.

The staff check matched 30/30 under the *different* analysis/hot_take/reaction taxonomy. It revealed no disagreements to classify as a consistency error, definition gap, or defensible alternative. It therefore supplies no observed staff-boundary error to explain the Hacker News misses. Because this check used AI and a different taxonomy, it does not establish independent human consistency or prove the question/statement labels are correct. Underfitting combined with imbalance is a plausible explanation, not a proven exclusion of label noise.

The zero-shot baseline's question F1 of 0.733 shows that these held-out requests are recognizable under the definitions. The before confidence gap can pass despite zero question recall: confident majority-label guesses are often correct statements, while less confident guesses include missed questions. Passing that target does not make the question classifier useful or establish probability calibration.

- **Accuracy miss:** The missed questions are enough to prevent the 0.75 accuracy target. The matrix and question recall identify the affected label; stable scores alone do not show the distinction was learned.
- **Question-F1 miss:** Confusing real requests with statements directly lowers question recall. The majority share and training behavior motivate a single optimizer-setting experiment; the perfect staff-set rate cannot rule out noise in this separate taxonomy.

The original five criteria are unchanged. No target was lowered after seeing a miss.

## Agreement Report

**Agreement rate:** **30 / 30 = 100%** against the instructor's `staff_labels.csv`. All 30 texts match; there are no missing posts.

`my_staff_labels.csv` was committed in `274bec1` before the answer key was copied from Downloads and opened. I used AI to apply the supplied staff taxonomy rather than the project's question/statement labels.

**Disagreements:** None. There are no cases to adjudicate or assign to piles (a), (b), or (c); no fictional disagreements have been added.

**Borderline decisions checked against the rules:**

- `sp_014`: **hot_take**. The 3% statistic accompanies an overconfident conclusion that shoes are the whole story. Rule 1 explicitly distinguishes a decorative number from a load-bearing argument.
- `sp_018`: **hot_take**. The eight-minute-mile threshold is an unsupported general cutoff, not supporting evidence. Rule 2 also rules out reaction because it is not an immediate personal experience.
- `sp_027`: **reaction**. The approximate 20-degree lean describes how the windy run felt; it does not support a general argument. Rules 1–3 keep a number alone from turning a personal reaction into analysis.

The set was relatively clear when the explicit rules were applied. This automated comparison on short running-forum posts is limited evidence; it does not independently validate the separate Hacker News dataset or human labeling consistency.

## The Improvement

**One change:** learning rate increased from `2e-5` to **`5e-5`**. Epochs (3), batch size (16), maximum length (128), model, dataset, taxonomy, criteria, and seeds were unchanged. Each after trial used exactly the same split as its paired before trial.

**Why this change:** The weak question boundary and attraction to the majority label suggested insufficient learning at the original setting. Raising only the learning rate tests whether larger updates help the model leave that solution. This was one predeclared trial, not a search over test-set settings; neither the labels nor the thresholds were edited to improve the scores.

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---:|---:|---:|---|
| 1. Overall accuracy | >=0.75 | 0.846 | 0.769 | 0.821 | MET |
| 2. Question F1 | >=0.65 | 0.769 | 0.667 | 0.667 | MET |
| 3. Statement F1 | >=0.75 | 0.885 | 0.824 | 0.877 | MET |
| 4. Dataset size/balance | >=200 unique; max share <=70% | 255; 68.24% max | 255; 68.24% max | 255; 68.24% max | MET |
| 5. Confidence gap | >=0.10 | 0.385 | 0.462 | 0.231 | MET |

### Paired comparison

| Seed | Accuracy before | Accuracy after | Change | Question F1 before | Question F1 after |
|---|---:|---:|---:|---:|---:|
| 42 | 0.692 | 0.846 | +0.154 | 0.000 | 0.769 |
| 7 | 0.692 | 0.769 | +0.077 | 0.000 | 0.667 |
| 2024 | 0.692 | 0.821 | +0.128 | 0.000 | 0.667 |

Mean accuracy changed by **+0.120**, and mean question F1 changed by **+0.701** across the same seeds. The higher learning rate helped these average scores, but each criterion still needs to hold in all three trials.

On the original seed-42 posts, after accuracy is 0.846 versus the baseline's 0.795. This is a like-for-like comparison; the baseline was not rerun on the other seeds' different test posts.

### Confusion matrix (after, seed 42)

| true \ predicted | question | statement |
|---|---:|---:|
| **question** | 10 | 2 |
| **statement** | 4 | 23 |

The baseline model cache is `.cache/huggingface`; `run_trials.py` selects it automatically. To reuse it with `baseline.py` in PowerShell, first set `$env:HF_HOME = "$PWD\.cache\huggingface"`.

The recorded runs used `python run_trials.py before` and `python run_trials.py after --learning-rate 5e-5`. To repeat them without overwriting evidence, append `--out .cache/recheck_before.json` or `--out .cache/recheck_after.json`. The runner preserves existing result files. The original Unit 5 `results.json` and `test_split.csv` remain unchanged.

## What's Still Broken

All five targets passed across these three trials. Generalization to new threads and independent human labels is still unmeasured.

**Gap between the intended distinction and what was learned:** The intended label identifies a real information request, including requests without a question mark and excluding rhetorical questions; seed 42 missed 12 questions before the change and 2 afterward. The after matrix measures improvement on this selected, AI-labeled sample, but its punctuation correlation and lack of independent human review prevent treating it as broad community performance.
