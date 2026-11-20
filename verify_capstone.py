"""Independently verify committed capstone evidence without rerunning training."""

import hashlib
import json
import math
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main():
    phases = {}
    all_ids = set()
    for phase in ("before", "after"):
        trials = read(f"capstone_evidence/{phase}_results.json")["trials"]
        assert [t["trial"] for t in trials] == [1, 2, 3]
        phases[phase] = []
        for trial in trials:
            records = [json.loads(line) for line in
                       (ROOT / trial["log"]).read_text(encoding="utf-8").splitlines()]
            requests = [r for r in records if r["event"] == "request"]
            assert len(requests) == 18
            by_id = {r["request_id"]: r for r in requests}
            assert len(by_id) == 18
            assert not all_ids.intersection(by_id)
            all_ids.update(by_id)
            assert len([r for r in records if r["event"] == "startup" and r["status"] == 200]) == 1
            measured = trial["valid"] + trial["invalid"] + [trial["recovery"]]
            assert len(measured) == 17
            for response in measured + [trial["warmup"]]:
                record = by_id[response["body"]["request_id"]]
                assert record["output"] == response["body"] and record["status"] == response["status"]
                assert "input" in record and datetime.fromisoformat(record["timestamp"]).utcoffset().total_seconds() == 0
                assert math.isfinite(record["cpu_seconds"]) and record["cpu_seconds"] >= 0
                assert 0 <= record["duration_seconds"] <= response["client_seconds"] + .001
            assert [r["status"] for r in trial["invalid"]] == [400]*5+[413]
            assert [r["body"]["error"]["code"] for r in trial["invalid"]] == [
                "missing_text", "empty_text", "invalid_text_type", "invalid_json",
                "invalid_encoding", "body_too_large"]
            assert trial["recovery"]["status"] == 200
            assert all(r["status"] == 200 for r in trial["valid"])
            assert all(r["body"]["label"] in ("question", "statement")
                       and 0 <= r["body"]["confidence"] <= 1 for r in trial["valid"])
            cost = sum(by_id[r["body"]["request_id"]]["cpu_seconds"] for r in trial["valid"]) / 10
            timely = sum(r["client_seconds"] <= .5 for r in trial["valid"])
            assert math.isclose(cost, trial["mean_cpu_seconds"], abs_tol=1e-12)
            expected = [True, True, timely >= 9, True, cost <= .5]
            assert expected == trial["criteria_met"]
            assert (trial["contracts"], trial["complete_logs"], trial["timely"], trial["rejected"]) == (10, 17, timely, 6)
            assert by_id[trial["warmup"]["body"]["request_id"]]["model_load_count"] == 1
            recovery_loads = by_id[trial["recovery"]["body"]["request_id"]]["model_load_count"]
            assert recovery_loads == (12 if phase == "before" else 1)
            phases[phase].append([by_id[r["body"]["request_id"]] for r in trial["valid"]])
    for old, new in zip(phases["before"], phases["after"]):
        for a, b in zip(old, new):
            assert a["input"] == b["input"]
            assert a["output"]["label"] == b["output"]["label"]
            assert abs(a["output"]["confidence"]-b["output"]["confidence"]) < 1e-6
    manifest = read("capstone_evidence/model_manifest.json")
    original = read("results_three_seeds_after.json")[0]
    assert manifest["regression_result"]["confusion"] == original["confusion"]
    assert manifest["regression_result"]["accuracy"] == original["accuracy"]
    weights = ROOT / "models/capstone/model.safetensors"
    if weights.exists():
        assert hashlib.sha256(weights.read_bytes()).hexdigest() == manifest["weights_sha256"]
    old_criteria = subprocess.check_output(["git", "show", "7d4b554:criteria.md"], cwd=ROOT, text=True, encoding="utf-8")
    assert (ROOT / "criteria_unit5.md").read_text(encoding="utf-8") == old_criteria
    subprocess.run(["git", "diff", "--exit-code", "7d4b554", "--", "labels.csv", "label_definitions.txt",
                    "results.json", "test_split.csv", "results_three_seeds_before.json",
                    "results_three_seeds_after.json", "baseline_results.json", "agreement_results.json"], cwd=ROOT, check=True)
    print("PASS: six real sessions, 108 request records, unchanged predictions, all verdicts and CPU means recomputed, checkpoint regression matched, and prior evidence preserved.")


if __name__ == "__main__":
    main()
