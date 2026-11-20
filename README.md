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


## Capstone


**What This Extends**


TakeMeter already classified Hacker News comments as question or statement. This extension adds a local HTTP run path, a small browser demo, structured logs, and measured operating cost. It does not add a new taxonomy or change the training data. The prepared checkpoint reproduces the already-tested Unit 6 seed-42 settings and confusion matrix; model preparation is setup, not the capstone improvement. Earlier criteria are preserved verbatim in [criteria_unit5.md](criteria_unit5.md).


**The Shape**


Shape **A — Deploy and instrument**, using **Path B — local with logs**. In scope: serve the existing model, reject bad inputs, record outcomes, document clean setup, and measure operation. Out of scope: cloud hosting, authentication, a review queue, new labels/data, model tuning, concurrent users and load testing. No stretch features are claimed.


**Running It**


After the setup in [RUNNING.md](RUNNING.md), the single start command is:


```powershell
.\.venv\Scripts\python.exe capstone.py
```


Open [the local demo](http://127.0.0.1:8765), or POST JSON to `/classify`. GET `/health` reports readiness. The service binds only to localhost and handles one request at a time. The browser form was also exercised through UI controls: the comment "Where can I find the documentation?" displayed QUESTION, confidence 70.4%, and the matching logged request ID. See [browser_check.json](capstone_evidence/browser_check.json).


Clean-checkout verification: **passed**, source revision `12a7b4d67a89d3ffc6e2750809d0b205bff4dbf5`, Python `3.11.1`, fresh isolated environment (no system site packages), and a newly prepared checkpoint. The record is [clean_checkout.json](capstone_evidence/clean_checkout.json). The first install exposed an old-pip/CPU-index dependency-resolution problem; the corrected instructions upgrade pip, install the CPU wheel separately, then install the full lock file.


The weight file is **267,832,560 bytes** (255.4 MiB), with tokenizer/config files adding under 2 MB. Weights stay outside Git in `models/capstone/`; the checksum and original-model regression result are in [model_manifest.json](capstone_evidence/model_manifest.json). Setup needs Python 3.11, Git, the pinned CPU dependencies, internet for initial public weight downloads, about 9 GB free disk and 6 GB RAM. Inference uses local files and no hosted model API.


**Instrumentation**


`capstone.py::Handler.finish_json` appends each classification or rejection to JSONL before writing the HTTP response. Fields are event, UTC timestamp, request_id, path, input, output, HTTP status, duration_seconds, cpu_seconds, and model_load_count. Startup has a separate record. Invalid JSON/UTF-8 and oversized input retain bounded diagnostic input information. The HTML page itself is a static asset, not a classification run.


Handler measurements start before validation and stop after response serialization, immediately before log append and HTTP write. Client measurements in `test_capstone.py::request` include the round trip, log append and response delivery. Logs therefore distinguish handler work from end-to-end latency.


Six real sessions generated **108 request records plus six startup records**: ten measured valid classifications, six deliberate invalid inputs, one recovery request and one excluded warm-up per session. Full sessions are committed under `capstone_evidence/`; live user logs append to ignored `logs/capstone.jsonl`.


Ten actual successful entries from `capstone_evidence/after_trial_1.jsonl` (not synthetic log examples):


```jsonl
{"event": "request", "timestamp": "2026-11-20T22:27:05.515372+00:00", "request_id": "54d52636-8f5f-47b8-a0f9-f8b245fbd15c", "path": "/classify", "input": {"text": "I've never played those mobile ad games and this scratched my curiosity. Now you're telling me they don't deliver and I'm curious again, how do they fail their delivery?"}, "output": {"request_id": "54d52636-8f5f-47b8-a0f9-f8b245fbd15c", "label": "statement", "confidence": 0.5184560418128967}, "status": 200, "duration_seconds": 0.0357454000004509, "cpu_seconds": 0.125, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.584383+00:00", "request_id": "272ff0a2-84ca-4603-8bac-a055f6bd7e4c", "path": "/classify", "input": {"text": "Its mostly useful for remote sessions as you can use one ssh connection for multiple terminals, and of course the most common usecase, leave processes running after you logout (or if the connection drops)."}, "output": {"request_id": "272ff0a2-84ca-4603-8bac-a055f6bd7e4c", "label": "statement", "confidence": 0.8912459015846252}, "status": 200, "duration_seconds": 0.04270790000009583, "cpu_seconds": 0.1875, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.610924+00:00", "request_id": "e0c8beb8-015a-4352-91d2-bafd1300969f", "path": "/classify", "input": {"text": "How are you setting the alerts? Are you using anomaly detection? If so, what kind?"}, "output": {"request_id": "e0c8beb8-015a-4352-91d2-bafd1300969f", "label": "question", "confidence": 0.7423256635665894}, "status": 200, "duration_seconds": 0.025444300001254305, "cpu_seconds": 0.0625, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.695500+00:00", "request_id": "925725e6-94df-4a76-a449-a43c002c0bfc", "path": "/classify", "input": {"text": "Wow, thanks to whoever posted this! I made this game.\nLike many, I was frustrated there's no new StarCraft coming till 2030, so I half-jokingly made the mini-game those mobile ads always promise and never deliver. Something you can play with one hand, that your friends who've never played StarCraft can just pick up.(Turns out you can squeeze a lot of extra gameplay/design on top of it.)\nAlso, if you're going to copy Blizzard you might as well copy the whole package right, so there's a CG trailer too: https://www.youtube.com/watch?v=rVDao71LC7A\nHonestly didn't expect people to grind this. I designed the endgame to be layer 50 and thought ppl can get at most ~70 if they really try, and somehow there are people on the leaderboard past 100 (without cheating). That's StarCraft players for you."}, "output": {"request_id": "925725e6-94df-4a76-a449-a43c002c0bfc", "label": "statement", "confidence": 0.9329322576522827}, "status": 200, "duration_seconds": 0.08214610000140965, "cpu_seconds": 0.375, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.775484+00:00", "request_id": "f36fd476-4200-4b76-a198-889e322a2405", "path": "/classify", "input": {"text": "I think analyzing and understanding bad people (or, let's say, people who are consistently harmful to those around them?) is valuable.\nI don't think seeking to involve those people in your life is. It would be interesting to ask an oracle what percentage of people have managed to \"change\" an abusive partner after pursuing them knowing full well the red flags they display. I'd wager it is a tiny percentage though."}, "output": {"request_id": "f36fd476-4200-4b76-a198-889e322a2405", "label": "statement", "confidence": 0.8590705990791321}, "status": 200, "duration_seconds": 0.06137250000028871, "cpu_seconds": 0.25, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.828006+00:00", "request_id": "71059731-9a91-423b-82c2-59c49ea7e737", "path": "/classify", "input": {"text": "It doesn't cease to amaze me how uncreative attackers are time and time again. A cryptominer in 2026? They really earned the three cents they are getting out of that."}, "output": {"request_id": "71059731-9a91-423b-82c2-59c49ea7e737", "label": "question", "confidence": 0.5244361758232117}, "status": 200, "duration_seconds": 0.036844800000835676, "cpu_seconds": 0.125, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:05.942533+00:00", "request_id": "4702b21b-aada-47ce-82b6-11aaccd24337", "path": "/classify", "input": {"text": "Is that a requirement though? If the AI used existing understanding/methods (which I assume it did) then there's nothing really \"new\" there, right? Shouldn't it be possible to get understanding from how the existing methods were used? Or, even knowing it's true, cull an incredible number of paths from the problem space around it, to make finding understanding easier?\nI'm not a mathematician, but I've always been able to find understandings from exploring the paths starting from either direction of the conceptual graph that exists between a \"problem\" and a \"solution\"."}, "output": {"request_id": "4702b21b-aada-47ce-82b6-11aaccd24337", "label": "question", "confidence": 0.6318862438201904}, "status": 200, "duration_seconds": 0.08944239999982528, "cpu_seconds": 0.359375, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:06.028067+00:00", "request_id": "7ba4b56a-2e85-466d-821a-738dfe1dd358", "path": "/classify", "input": {"text": "> The AMD hardware is x86_64, which means lower battery life on average for normal users [...]\nA Ryzen AI Max+ 395 powered tablet with 70Wh [0] gets the same battery life given the same task as a Nvidia N1X powered laptop with 99.9 Wh [1].\nPower Consumption in their \"Cyberpunk / Stress Test\" is also lower at Ø109.3 (108.8-110.8) Watt for the x86_64 vs Ø134.5 (132.1-137.5) Watt for the arm64 system using the same settings, resolution and display brightness. They also get the same performance when normalising for resolutions and settings in Cyberpunk, so this is not an instance of one providing significantly more performance.\n[0] https://www.notebookcheck.net/Asus-ROG-Flow-Z13-GZ302EA-Conv...\n[1] https://www.notebookcheck.net/Asus-ProArt-P16-RTX-Spark-Lapt..."}, "output": {"request_id": "7ba4b56a-2e85-466d-821a-738dfe1dd358", "label": "statement", "confidence": 0.8505184054374695}, "status": 200, "duration_seconds": 0.08147549999921466, "cpu_seconds": 0.3125, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:06.061074+00:00", "request_id": "eb7249f8-00b9-4584-bb31-247edbd8337d", "path": "/classify", "input": {"text": "Yep, many hay barns have caught fire because the hay was bailed while too wet and it is fermenting so vigorously."}, "output": {"request_id": "eb7249f8-00b9-4584-bb31-247edbd8337d", "label": "statement", "confidence": 0.8730511665344238}, "status": 200, "duration_seconds": 0.03143090000230586, "cpu_seconds": 0.125, "model_load_count": 1}
{"event": "request", "timestamp": "2026-11-20T22:27:06.136599+00:00", "request_id": "91b578b8-9422-43aa-99ff-c2420a7fa9d7", "path": "/classify", "input": {"text": "I'm in what I think will be my last tech job before retraining into something else. The aspects I like about the work are gone, I'm coasting at a small company that's not a great fit, has a visa cliff, and is poorly paid, and the steps it would take to become competitive in an LLM driven tech job market are less appealing to me than the steps it would take to switch over to a different career (likely in healthcare)."}, "output": {"request_id": "91b578b8-9422-43aa-99ff-c2420a7fa9d7", "label": "statement", "confidence": 0.9229776859283447}, "status": 200, "duration_seconds": 0.07441739999921992, "cpu_seconds": 0.3125, "model_load_count": 1}
```


One actual rejected-input entry from the same session:


```json
{
  "event": "request",
  "timestamp": "2026-11-20T22:27:06.139597+00:00",
  "request_id": "f2d104b2-1fcb-4aad-9d72-8e15d38610e3",
  "path": "/classify",
  "input": {},
  "output": {
    "request_id": "f2d104b2-1fcb-4aad-9d72-8e15d38610e3",
    "error": {
      "code": "missing_text"
    }
  },
  "status": 400,
  "duration_seconds": 9.059999865712598e-05,
  "cpu_seconds": 0.0,
  "model_load_count": 1
}
```


**What It Costs**


Cost is **measured process CPU time**, not an invented dollar price. Each trial averages its ten measured warm valid requests. Before means were 0.7203, 0.7406, 0.7312 CPU seconds; after means were 0.2234, 0.2313, 0.2281. Pooling the three equal-size trials gives **0.2276 CPU seconds per warm classification** (30 measured requests). Mean client wall time is **0.0674 seconds**, separately measured.


For **100 people/day, one classification each**, a running process needs approximately `100 × 0.227604 = 22.76` measured warm handler CPU seconds/day. If restarted once daily, add average startup CPU 7.4583 s and first-request warm-up CPU 0.8958 s: approximately **31.11 CPU seconds/day** within these measurement boundaries. Startup + first request are excluded from the warm target but explicitly included in this cold-start calculation. This does not price electricity, idle RAM, training/setup, or HTTP/logging CPU outside the stated boundary. No inference API calls or token charges occur.


**Run Log and Verdicts**


The five targets were committed in `4384dee`, with the measurement boundary clarified in `1a8efd7`, before the first results commit `ed13a95`. No targets were lowered. Three fresh processes per phase used the same checkpoint, four CPU threads and the same ten existing held-out comments plus fixed invalid/recovery cases. Warm-up is logged and excluded from warm performance criteria.


| Criterion | Target | Trial 1 | Trial 2 | Trial 3 | Verdict |
|---|---|---|---|---|---|
| 1. Valid prediction contract | 10/10 | 10/10 | 10/10 | 10/10 | MET |
| 2. Complete request logs | 17/17 + warm-up | 17/17 | 17/17 | 17/17 | MET |
| 3. Warm client latency | >=9/10 within 0.50 s | 10/10 | 10/10 | 10/10 | MET |
| 4. Invalid inputs + recovery | 6/6 + HTTP 200 recovery | 6/6; recovery 200 | 6/6; recovery 200 | 6/6; recovery 200 | MET |
| 5. Mean warm CPU cost | <=0.50 CPU s | 0.7203 s | 0.7406 s | 0.7312 s | MISSED |


Criterion 2 repeats the complete logging check, including a separate warm-up record verified by `verify_capstone.py`. Every numeric target must hold in every trial.


Real criterion evidence from trial 1 is below. Response and client timings come from `test_capstone.py::request`; counts and CPU means come from `test_capstone.py::trial`. Field extracts are taken from `capstone_evidence/before_results.json`; full raw request logs are in `before_trial_1.jsonl`.


1. **Prediction contract:** actual response from `capstone.py::Handler.do_POST`.


```json
{
  "status": 200,
  "body": {
    "request_id": "c1a44a99-4f8b-4b99-949d-4a7c7eccb9e7",
    "label": "statement",
    "confidence": 0.5184560418128967
  },
  "client_seconds": 0.15372220000062953
}
```


2. **Logging:** the measured response IDs each matched one `Handler.finish_json` record.


```json
{
  "trial": 1,
  "complete_logs": 17
}
```


3. **Latency:** actual first client duration and count within 0.50 s.


```json
{
  "client_seconds": 0.15372220000062953,
  "timely": 10
}
```


4. **Bad paths:** actual six rejection responses, followed by the actual recovery response.


```json
{
  "invalid": [
    {
      "status": 400,
      "body": {
        "request_id": "0d18ba2a-7388-4915-afd1-405ccfd1c2a6",
        "error": {
          "code": "missing_text"
        }
      },
      "client_seconds": 0.0018939000001410022
    },
    {
      "status": 400,
      "body": {
        "request_id": "9f6bb87f-1a73-46d3-9b52-04eceec1e79a",
        "error": {
          "code": "empty_text"
        }
      },
      "client_seconds": 0.024040899999818066
    },
    {
      "status": 400,
      "body": {
        "request_id": "c76d5c11-3aee-452a-b65b-4eea66a443d3",
        "error": {
          "code": "invalid_text_type"
        }
      },
      "client_seconds": 0.0016891999985091388
    },
    {
      "status": 400,
      "body": {
        "request_id": "cf5019e7-2633-4a47-bc60-3ce57a7128f1",
        "error": {
          "code": "invalid_json"
        }
      },
      "client_seconds": 0.014633200000389479
    },
    {
      "status": 400,
      "body": {
        "request_id": "eadf3e5e-e5d8-4fa6-b119-ecc72e86c96f",
        "error": {
          "code": "invalid_encoding"
        }
      },
      "client_seconds": 0.0016093999984150287
    },
    {
      "status": 413,
      "body": {
        "request_id": "c59d219a-8f15-4a75-bac8-a9d666618e7f",
        "error": {
          "code": "body_too_large"
        }
      },
      "client_seconds": 0.0016515000024810433
    }
  ],
  "recovery": {
    "status": 200,
    "body": {
      "request_id": "85573586-30c4-4820-9827-6f1dbf3b1537",
      "label": "question",
      "confidence": 0.7043129801750183
    },
    "client_seconds": 0.1705251000021235
  }
}
```


5. **CPU cost:** actual mean of ten logged request CPU measurements.


```json
{
  "mean_cpu_seconds": 0.7203125
}
```


**Diagnosis:** Criteria 1–4 were met in every initial trial. Criterion 5 was **MISSED** in all three. The responsible stage was `capstone_model.py::Predictor.predict`: it called `from_pretrained` for the same local tokenizer and weights for every valid request. The load counter rose from 1 at warm-up to 12 at recovery in each session. Repeated loading/deserialization and allocation consumed CPU even though client latency already met its looser target. This is an operational-loading cost, not evidence that the model-quality targets changed.


**The Improvement**


One change: keep the model and tokenizer in the service process and reuse them for inference. The plan was filed with the before results in `ed13a95`; the implementation is `468f3aa`. The runtime serving change relative to `52b32f2` is only asset reuse in `capstone_model.py`. Model weights, data, taxonomy, thread count, request cases, input rules and criteria stayed fixed. The test harness later gained an alternate output-directory flag solely to preserve evidence during independent reruns.


| Criterion | Target | Trial 1 | Trial 2 | Trial 3 | Verdict |
|---|---|---|---|---|---|
| 1. Valid prediction contract | 10/10 | 10/10 | 10/10 | 10/10 | MET |
| 2. Complete request logs | 17/17 + warm-up | 17/17 | 17/17 | 17/17 | MET |
| 3. Warm client latency | >=9/10 within 0.50 s | 10/10 | 10/10 | 10/10 | MET |
| 4. Invalid inputs + recovery | 6/6 + HTTP 200 recovery | 6/6; recovery 200 | 6/6; recovery 200 | 6/6; recovery 200 | MET |
| 5. Mean warm CPU cost | <=0.50 CPU s | 0.2234 s | 0.2313 s | 0.2281 s | MET |


| Measure | Before mean | After mean |
|---|---:|---:|
| Warm CPU seconds/request | 0.7307 | 0.2276 |
| Client wall seconds/request | 0.1987 | 0.0674 |


CPU cost fell **68.9%** and mean client latency fell **66.1%**. All five criteria now pass across all three trials. Model load count stays at 1 after warm-up. `verify_capstone.py` also compares every before/after prediction: labels are identical and confidence differs by less than 1e-6. The improvement reduces work; it does not claim better classification accuracy. Keeping weights resident uses memory between requests, which is the explicit trade-off.


**What's Still Broken**


All five current targets were met after caching. The 0.50-second mean CPU budget is now generous; the next version would test a **0.30-second** budget, without changing this unit's filed target. The model still has the Unit 6 semantic errors (seed 42 missed two questions and called four statements questions). Caching does not fix those errors.


This is a serial local service, not a multi-user deployment. Logs are local files without rotation or a retention policy; disk-full/permission loss during logging is not validated by the six input-error tests. Independent human label review and generalization to new threads remain unmeasured. Work stopped after one isolated measured operational change to keep its effect identifiable.


The first next step would be independent review of the rhetorical-question boundary, because inference is now inexpensive but incorrect labels still limit usefulness. I would establish that evidence before changing training data or adding a review queue.


**How I Used AI**


1. I directed a bounded local extension and used AI to implement the model adapter, serving layer, browser demo and logs. The scope kept the existing taxonomy/data and excluded cloud hosting, a review queue and model tuning.


2. I used AI to run real operational trials, diagnose repeated model loading, implement the single cache change, repair the clean setup instructions, and draft the measured report. The original and corrected results are retained; misses were not removed. The five capstone criteria were AI-drafted before tests and are not represented as unaided student-authored criteria.
