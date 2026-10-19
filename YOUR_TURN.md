# Your part before training

This is preparation, not a finished submission.

1. Read the two definitions and boundary rule in [README.md](README.md).
   Read the community yourself and adjust the definitions if needed.
2. Label the 20 posts in [data/cold_labeling.md](data/cold_labeling.md)
   without AI. Write `question` or `statement` under each post.
   Alternatively, fill the label column in `data/cold_labels.csv`.
3. Write your five original numeric criteria and reasons in
   [criteria.md](criteria.md), covering at least three areas. No results
   have been generated, so you can still set these before training.
4. Tell Codex when both files are finished. It can check clarity, commit your
   criteria before training, and pre-label the remaining 200 comments.
   Read and correct every pre-labeled comment before training.

After that, Codex can assemble the final unsplit `labels.csv`, verify label
balance and duplicates, run the starter notebook sections 1-5, save actual
`results.json` and `test_split.csv`, finish the README, and push the result.
Do not submit the repository as complete before those steps are finished.

Your fork: https://github.com/7dracoder/ai201-project3-takemeter-starter-v2026

The assignment specifically reserves the five criteria and first 20 labels
for you. AI-generated criteria or labels cannot honestly be called your
original criteria or unaided cold labels.
