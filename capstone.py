"""Single-process local TakeMeter service: python capstone.py."""

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_BODY = 16_384
MAX_TEXT = 4_000


def append_record(path, record):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def finish_json(self, status, output, incoming, started, cpu_started, request_id):
        output = {"request_id": request_id, **output}
        body = json.dumps(output, allow_nan=False).encode("utf-8")
        record = {
            "event": "request", "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id, "path": self.path, "input": incoming,
            "output": output, "status": status,
            "duration_seconds": time.perf_counter() - started,
            "cpu_seconds": time.process_time() - cpu_started,
            "model_load_count": self.server.predictor.load_count,
        }
        append_record(self.server.log_path, record)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = (ROOT / "capstone_demo.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        started, cpu = time.perf_counter(), time.process_time()
        request_id = str(uuid.uuid4())
        if self.path == "/health":
            self.finish_json(200, {"ready": True}, None, started, cpu, request_id)
        else:
            self.finish_json(404, {"error": {"code": "not_found"}}, None, started, cpu, request_id)

    def do_POST(self):
        started, cpu = time.perf_counter(), time.process_time()
        request_id = str(uuid.uuid4())
        incoming = None
        self.connection.settimeout(10)

        def reject(code, status=400):
            self.finish_json(status, {"error": {"code": code}}, incoming, started, cpu, request_id)

        try:
            if self.path != "/classify":
                reject("not_found", 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                reject("invalid_length")
                return
            if length < 0:
                reject("invalid_length")
                return
            raw = self.rfile.read(min(length, MAX_BODY + 1))
            incoming = {"bytes": length, "raw_hex_prefix": raw[:64].hex()}
            if length > MAX_BODY:
                reject("body_too_large", 413)
                return
            try:
                decoded = raw.decode("utf-8")
            except UnicodeDecodeError:
                reject("invalid_encoding")
                return
            incoming = decoded
            try:
                incoming = json.loads(decoded)
            except json.JSONDecodeError:
                reject("invalid_json")
                return
            if not isinstance(incoming, dict) or "text" not in incoming:
                reject("missing_text")
                return
            text = incoming["text"]
            if not isinstance(text, str):
                reject("invalid_text_type")
                return
            if not text.strip():
                reject("empty_text")
                return
            if len(text) > MAX_TEXT:
                reject("text_too_long")
                return
            output = self.server.predictor.predict(text)
            self.finish_json(200, output, incoming, started, cpu, request_id)
        except TimeoutError:
            reject("request_timeout", 408)
        except (BrokenPipeError, ConnectionResetError):
            # finish_json writes the record before attempting the response.
            return
        except Exception as error:
            self.finish_json(500, {"error": {"code": "prediction_failed", "type": type(error).__name__}},
                             incoming, started, cpu, request_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model-dir", type=Path, default=ROOT / "models" / "capstone")
    parser.add_argument("--log", type=Path, default=ROOT / "logs" / "capstone.jsonl")
    args = parser.parse_args()
    args.log.parent.mkdir(parents=True, exist_ok=True)
    started, cpu = time.perf_counter(), time.process_time()
    try:
        from capstone_model import Predictor
        predictor = Predictor(args.model_dir)
        server = HTTPServer(("127.0.0.1", args.port), Handler)
    except Exception as error:
        append_record(args.log, {"event": "startup", "timestamp": datetime.now(timezone.utc).isoformat(),
                      "input": {"port": args.port}, "output": {"error": type(error).__name__},
                      "status": 500, "duration_seconds": time.perf_counter()-started,
                      "cpu_seconds": time.process_time()-cpu})
        raise SystemExit(f"Startup failed: {error}")
    server.predictor, server.log_path = predictor, args.log
    append_record(args.log, {"event": "startup", "timestamp": datetime.now(timezone.utc).isoformat(),
                  "input": {"port": args.port}, "output": {"ready": True}, "status": 200,
                  "duration_seconds": time.perf_counter()-started,
                  "cpu_seconds": time.process_time()-cpu})
    print(f"TakeMeter ready: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
