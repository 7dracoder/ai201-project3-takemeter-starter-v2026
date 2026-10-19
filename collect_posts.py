"""Collect public Hacker News comments for TakeMeter; never invent posts."""

import csv
import html
import json
import random
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen


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
    posts, seen = [], set()
    # Freeze the collection window so reruns do not drift to newer comments.
    for page in range(5):
        url = (
            "https://hn.algolia.com/api/v1/search_by_date?tags=comment"
            f"&hitsPerPage=100&page={page}&numericFilters=created_at_i<1792454400"
        )
        with urlopen(url, timeout=60) as response:
            hits = json.load(response)["hits"]
        for hit in hits:
            parser = PlainText()
            parser.feed(hit.get("comment_text") or "")
            text = html.unescape("".join(parser.parts)).strip()
            if len(text.split()) < 10 or text in seen:
                continue
            seen.add(text)
            posts.append({
                "text": text,
                "url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                "created_at": hit["created_at"],
            })
    random.Random(42).shuffle(posts)
    cold = posts[:20]
    remaining = posts[20:]
    # Sample by punctuation to find enough candidates for each label.
    questions = [p for p in remaining if "?" in p["text"]][:100]
    statements = [p for p in remaining if "?" not in p["text"]][:100]
    selected = cold + questions + statements
    Path("data/collected_posts.json").write_text(
        json.dumps(selected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with open("data/cold_labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "note"])
        writer.writeheader()
        for post in cold:
            writer.writerow({"text": post["text"], "label": "", "note": ""})
    print(f"Collected {len(selected)} whole comments, including 20 unlabeled rows.")
    print(f"Other candidates: {len(questions)} with ?, {len(statements)} without ?.")


if __name__ == "__main__":
    main()
