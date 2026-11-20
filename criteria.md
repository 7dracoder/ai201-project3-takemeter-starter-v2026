# Capstone acceptance criteria

Shape A: the existing TakeMeter classifier gains a local serving and
observability layer. These AI-drafted targets are filed before capstone tests;
they are not presented as unaided student work. The previous project's exact
criteria are preserved in criteria_unit5.md and Git history.

A trial starts a fresh service process and sends one warm-up classification,
then ten valid requests, six invalid requests, and one valid recovery request.
The warm-up is logged but excluded from warm latency/cost targets. All targets
must hold in each of three trials, before and after one measured improvement.

1. **Valid requests: 10/10 return HTTP 200 and the prediction contract.**
   Every one of the ten valid requests must return a unique request_id,
   label question or statement, and finite confidence in [0,1].
   Reason: an operational wrapper must reliably expose the existing model's
   result; this measures serving correctness, not a new accuracy claim.

2. **Observability: 17/17 measured requests have exactly one complete log.**
   Match the ten valid, six invalid, and one recovery response IDs to exactly
   one JSONL request record each, containing UTC timestamp, input, output,
   HTTP status, duration_seconds >=0, and cpu_seconds >=0. Error records must
   include a named error code. A separate warm-up record is also required.
   Reason: a missing failure is a blind spot, and duplicate logs inflate counts.

3. **Warm latency: at least 9/10 valid requests finish within 0.50 seconds.**
   Use client-measured end-to-end wall time on localhost, after the one
   excluded warm-up, with one request at a time and a 10-second client timeout.
   Reason: half a second makes a short-comment demo responsive on this CPU,
   while allowing one scheduling outlier. Cold startup is a different measure.

4. **Failure handling: 6/6 invalid requests are rejected, then recovery works.**
   Missing text, blank text, non-string text, malformed JSON, and invalid UTF-8
   must each return HTTP 400; a body larger than 16,384 bytes must return 413.
   Each response must be JSON with request_id and error.code. A subsequent
   valid request must return 200, proving the service remains usable.
   Reason: callers make mistakes, and a rejected input must leave a visible
   record without taking down the classifier or becoming an unexplained 500.

5. **Warm compute cost: mean CPU time is at most 0.50 seconds per request.**
   Average the logged cpu_seconds of the ten measured valid requests in a
   trial. Use time.process_time(), including validation, prediction, JSON
   serialization and the log append up to the recorded measurement boundary.
   Report the wall time separately. Do not count setup/training or the warm-up
   in the warm average; report cold costs separately rather than hiding them.
   Reason: this gives a budget of at most 50 CPU seconds for 100 daily
   classifications while making a local, measured claim without inventing a
   dollar or electricity price.

All five targets concern the operational extension. None replaces the original
model-quality targets, and a missed capstone target will not be lowered.
