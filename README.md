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

**Status:** 220 real comments collected. The student's 20 cold labels, five
acceptance criteria, review of the other labels, and training are pending.
Start with [YOUR_TURN.md](YOUR_TURN.md). No training results have been generated.

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

**Candidate distinctions observed in an AI reading of 45 collected comments:**
Some ask for practical advice; some give explanations or personal experience;
some phrase disagreement as a rhetorical question. The two-label choice keeps
this basic while making the last distinction explicit. This does not replace
the student's community reading.

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

**Sampling:** Five API pages, shuffled with seed 42. The first 20 are reserved
unlabeled for the student's cold pass. The other 200 comprise 100 comments
containing `?` and 100 without it, as a way to find candidate questions and
statements. Punctuation is a sampling hint, not a final label. This deliberately
selected sample does not estimate Hacker News's natural label frequencies.

**Labeling:** Not completed. `data/cold_labels.csv` has exactly 20 blank labels.
The student must label these unaided first. AI may then pre-label the other
200, but the student must read and correct every row. Only genuinely completed
unaided labels should receive `cold` in the note column. The final `labels.csv`
will be one unsplit file with `text,label,note` columns.

**Counts per label:** Pending labeling; 220 comments collected in total.
The final dataset must keep every label at or below 70%.

**Three candidate hard cases identified by AI (student review pending):**

1. [Quoted question followed by an answer](https://news.ycombinator.com/item?id=50158399):
   the comment quotes a question about StarCraft assets and answers "Because
   it's cool." Candidate labels: question/statement. AI choice: `statement`,
   because the author's own words are an answer.
2. [Self-answered purchasing question](https://news.ycombinator.com/item?id=50158645):
   the author asks why they would buy the RTX Spark, then explains why they
   prefer the DGX Spark. Candidate labels: question/statement. AI choice:
   `statement`, because the question introduces the author's own conclusion.
3. [An opinion followed by a request](https://news.ycombinator.com/item?id=50158542):
   the author enjoyed a video but asks whether clipping was a camera bug.
   Candidate labels: question/statement. AI choice: `question`, because the
   author requests clarification that the comment does not resolve.

## The Training Run

**Base model:** `distilbert-base-uncased`.

**Settings:** 3 epochs, learning rate `2e-5`, batch size 16, maximum length
128 tokens, seed 42. No hyperparameter changes planned.

**Split:** The starter notebook will make its stratified 70/15/15 split after
labeling. Raw posts remain whole; the tokenizer truncates model inputs to 128
tokens. Split counts, test-label support, and device will be recorded after
an actual run. No metrics are claimed yet.

**Pending:** Commit the student's completed criteria and final labels before
running notebook sections 1–5. Sections 6–7 belong to Unit 6.

## How I Used AI

**Moment 1:** I asked Codex to help complete the assignment with basic changes.
It read the instructions and starter files, collected public comments with
source links, and prepared blank worksheets. The student must still supply
original criteria and cold labels; AI has not filled those in.

**Moment 2:** Codex proposed a two-label taxonomy, identified quoted and
rhetorical questions as the difficult boundary, and generated eight synthetic
boundary examples. Those examples are explicitly excluded from collected data.
Student review and any resulting definition changes are still pending.

**Pre-labeling disclosure:** The reserved 20 comments have not been labeled
by AI. No remaining batch has been pre-labeled yet. Sampling comments by a
question mark is not semantic annotation. Future AI-assisted labels and the
student's review must be disclosed here when they happen.

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
