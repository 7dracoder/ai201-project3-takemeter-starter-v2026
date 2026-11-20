"""Measure three real service sessions; python test_capstone.py --phase before."""

import argparse
import collections
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def request(base, raw, timeout=10):
    started = time.perf_counter()
    req = Request(base + "/classify", data=raw, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            status, body = response.status, response.read()
    except HTTPError as response:
        status, body = response.code, response.read()
    return {"status": status, "body": json.loads(body),
            "client_seconds": time.perf_counter() - started}


def stop(process):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        process.terminate()
    process.wait(timeout=15)


def trial(phase, number, texts, evidence):
    log = evidence / f"{phase}_trial_{number}.jsonl"
    if log.exists():
        raise FileExistsError(f"Preserving existing log: {log}")
    console = ROOT / ".cache" / f"capstone_{phase}_{number}.log"
    console.parent.mkdir(exist_ok=True)
    with console.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen([sys.executable, "-u", str(ROOT / "capstone.py"),
                                    "--port", "0", "--log", str(log)], cwd=ROOT,
                                   stdout=stream, stderr=stream,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"Service exited; inspect {console}")
                match = re.search(r"TakeMeter ready: (http://127\.0\.0\.1:\d+)",
                                  console.read_text(encoding="utf-8", errors="replace"))
                if match:
                    base = match.group(1)
                    break
                time.sleep(.1)
            else:
                raise TimeoutError("Service did not start within 180 seconds")
            warmup = request(base, json.dumps({"text": texts[0]}).encode())
            valid = [request(base, json.dumps({"text": text}).encode()) for text in texts]
            bad = [b'{}', b'{"text":"   "}', b'{"text":42}', b'{',
                   b'{"text":"\xff"}', b'x' * 16_385]
            invalid = [request(base, body) for body in bad]
            recovery = request(base, b'{"text":"Where can I find the documentation?"}')
        finally:
            stop(process)
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    by_id = collections.defaultdict(list)
    for record in records:
        if record["event"] == "request":
            by_id[record["request_id"]].append(record)
    measured = valid + invalid + [recovery]
    complete = 0
    for response in measured:
        rid = response["body"].get("request_id")
        found = by_id[rid]
        if len(found) != 1:
            continue
        record = found[0]
        required = {"timestamp", "input", "output", "status", "duration_seconds", "cpu_seconds"}
        if (required <= record.keys() and record["status"] == response["status"]
                and record["output"] == response["body"]
                and record["duration_seconds"] >= 0 and record["cpu_seconds"] >= 0
                and (record["status"] < 400 or record["output"].get("error", {}).get("code"))):
            complete += 1
    contracts = sum(response["status"] == 200
                    and response["body"].get("label") in ("question", "statement")
                    and isinstance(response["body"].get("confidence"), (float, int))
                    and math.isfinite(response["body"]["confidence"])
                    and 0 <= response["body"]["confidence"] <= 1 for response in valid)
    ids = [response["body"].get("request_id") for response in valid]
    if len(set(ids)) != 10:
        contracts = 0
    rejected = sum(response["status"] == status
                   and bool(response["body"].get("request_id"))
                   and bool(response["body"].get("error", {}).get("code"))
                   for response, status in zip(invalid, [400]*5+[413]))
    cpu = [by_id[response["body"]["request_id"]][0]["cpu_seconds"] for response in valid]
    mean_cpu = sum(cpu)/len(cpu)
    timely = sum(response["client_seconds"] <= .5 for response in valid)
    result = {
        "trial": number, "contracts": contracts, "complete_logs": complete,
        "timely": timely, "rejected": rejected, "recovery_status": recovery["status"],
        "mean_cpu_seconds": mean_cpu,
        "mean_client_seconds": sum(r["client_seconds"] for r in valid)/10,
        "warmup": warmup, "valid": valid, "invalid": invalid, "recovery": recovery,
        "criteria_met": [contracts == 10, complete == 17, timely >= 9,
                         rejected == 6 and recovery["status"] == 200, mean_cpu <= .5],
        "log": str(log.relative_to(ROOT)),
    }
    print(f"{phase} trial {number}: met={result['criteria_met']}, "
          f"mean CPU={mean_cpu:.4f}s, mean client={result['mean_client_seconds']:.4f}s", flush=True)
    return result


def main():
    import csv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["before", "after"], required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "capstone_evidence")
    args = parser.parse_args()
    os.chdir(ROOT)
    evidence = args.output_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    output = evidence / f"{args.phase}_results.json"
    if output.exists():
        raise FileExistsError(f"Preserving existing results: {output}")
    with (ROOT / "test_split.csv").open(encoding="utf-8", newline="") as stream:
        texts = [r["text"] for r in csv.DictReader(stream) if len(r["text"]) <= 4_000][:10]
    assert len(texts) == 10
    results = []
    for number in (1, 2, 3):
        results.append(trial(args.phase, number, texts, evidence))
        output.write_text(json.dumps({"phase": args.phase, "trials": results}, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
