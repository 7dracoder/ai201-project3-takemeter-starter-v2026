"""Collect public Hacker News comments for TakeMeter; never invent posts."""

import argparse
import csv
import hashlib
import html
import json
import random
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / ".cache" / "hn_pages"
DEFAULT_PAGES = 5
PAGE_SIZE = 100
BUCKET_SIZE = 100
COLD_COUNT = 20
SEED = 42
CUTOFF = 1792454400
MIN_WORDS = 10
MAX_ATTEMPTS = 3


def fetch_page(url):
    """Cache each successful page and retry only transient failures."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))["hits"]
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(url, timeout=60) as response:
                payload = json.load(response)
            if not isinstance(payload.get("hits"), list):
                raise ValueError("API response has no hits list")
            temporary = cache.with_suffix(".tmp")
            temporary.write_text(json.dumps(payload), encoding="utf-8")
            temporary.replace(cache)
            return payload["hits"]
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(2 ** attempt)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br"):
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    parser.add_argument("--per-bucket", type=int, default=BUCKET_SIZE)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    if args.pages < 1 or args.per_bucket < 1:
        parser.error("pages and per-bucket must be positive")
    output = args.output_dir
    if any((output / name).exists() for name in ("collected_posts.json", "cold_labels.csv")):
        parser.error("Output already exists; choose another --output-dir to preserve annotations.")
    posts, seen = [], set()
    # Freeze the collection window so reruns do not drift to newer comments.
    for page in range(args.pages):
        url = (
            "https://hn.algolia.com/api/v1/search_by_date?tags=comment"
            f"&hitsPerPage={PAGE_SIZE}&page={page}&numericFilters=created_at_i<{CUTOFF}"
        )
        hits = fetch_page(url)
        for hit in hits:
            parser = PlainText()
            parser.feed(hit.get("comment_text") or "")
            text = html.unescape("".join(parser.parts)).strip()
            if len(text.split()) < MIN_WORDS or text in seen:
                continue
            seen.add(text)
            posts.append({
                "text": text,
                "url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                "created_at": hit["created_at"],
            })
    random.Random(SEED).shuffle(posts)
    cold = posts[:COLD_COUNT]
    remaining = posts[COLD_COUNT:]
    # Sample by punctuation to find enough candidates for each label.
    questions = [p for p in remaining if "?" in p["text"]][:args.per_bucket]
    statements = [p for p in remaining if "?" not in p["text"]][:args.per_bucket]
    if len(cold) != COLD_COUNT or min(len(questions), len(statements)) < args.per_bucket:
        raise ValueError(
            f"Too few comments: cold={len(cold)}, with ?={len(questions)}, "
            f"without ?={len(statements)}; increase --pages. Successful pages are cached."
        )
    selected = cold + questions + statements
    output.mkdir(parents=True, exist_ok=True)
    (output / "collected_posts.json").write_text(
        json.dumps(selected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (output / "cold_labels.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "note"])
        writer.writeheader()
        for post in cold:
            writer.writerow({"text": post["text"], "label": "", "note": ""})
    print(f"Collected {len(selected)} whole comments, including {COLD_COUNT} unlabeled rows.")
    print(f"Other candidates: {len(questions)} with ?, {len(statements)} without ?.")


if __name__ == "__main__":
    main()
