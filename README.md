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
committed before training. The collection, annotation, criteria, and execution
are AI-assisted; the disclosure below explains what was done.

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

**Three distinctions observed during the AI reading:** Some comments ask for
practical advice, some provide explanations or personal experience, and some
phrase disagreement as a rhetorical question. Two labels keep the task basic;
the boundary rule separates genuine requests from rhetorical statements.

**AI stress test (synthetic; excluded from the dataset):**

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

**Labeling:** AI read the full comments and assigned one semantic label to
each. Every note records `AI-labeled`, the source URL, and a reason. There was
no unaided human cold-labeling pass or independent human review; no row is
marked `cold`. The earlier blank cold-label worksheets are not training data.
`labels.csv` is the one unsplit dataset; the notebook creates the split.

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
have not been lowered to fit it. Further diagnosis and comparison across seeds
belong to Unit 6; those sections below remain blank.

**Before training:** Criteria were committed in `0b7abed` and the final dataset
in `38f619e`, before the notebook generated the results.

## How I Used AI

1. AI collected real public comments, proposed the two labels, and tested the
   difficult boundary with eight synthetic examples. Those synthetic examples
   are not part of the dataset. Semantic annotation changed many punctuation
   candidates into statements and prompted collection of 35 more questions.
2. AI drafted the five numeric criteria and reasons before training, labeled
   the comments, and ran the local notebook. It also added retries, page
   caching, sample-size checks, and protection against overwriting annotations
   to the collector after the grading feedback.

**Pre-labeling disclosure:** All 255 annotations are AI-generated. No unaided
student cold-labeling pass, student-authored criteria, independent human review,
or agreement score is claimed. These personal course requirements still need
student participation; the files and real model run do not substitute for it.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
