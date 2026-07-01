#!/usr/bin/env python3
"""
Append collected raw Reddit text into worldcup_dataset.csv as UNLABELED rows.

Collect posts/comments into a plain .txt file, one example per block,
separated by a blank line. Example raw.txt:

    Spain looked completely disorganized in midfield today.

    I think Brazil takes this whole tournament.

    WHAT A SAVE!!!

Then:
    python3 add_examples.py raw.txt

New rows are added with empty label/notes (ready for annotate.py).
Exact-duplicate text already in the dataset is skipped automatically.
"""

import csv
import os
import sys

DATASET = "worldcup_dataset.csv"
COLUMNS = ["text", "label", "notes"]


def existing_texts(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {(r.get("text") or "").strip() for r in csv.DictReader(f)}


def parse_blocks(raw_path):
    with open(raw_path, encoding="utf-8") as f:
        content = f.read()
    blocks = [b.strip() for b in content.split("\n\n")]
    return [b.replace("\n", " ").strip() for b in blocks if b.strip()]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_examples.py raw.txt [dataset.csv]")
        sys.exit(1)
    raw_path = sys.argv[1]
    dataset = sys.argv[2] if len(sys.argv) > 2 else DATASET

    seen = existing_texts(dataset)
    blocks = parse_blocks(raw_path)

    new_rows, dupes = [], 0
    for b in blocks:
        if b in seen:
            dupes += 1
            continue
        seen.add(b)
        new_rows.append({"text": b, "label": "", "notes": ""})

    file_exists = os.path.exists(dataset)
    with open(dataset, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        for r in new_rows:
            writer.writerow(r)

    print(f"Parsed {len(blocks)} blocks from {raw_path}")
    print(f"Added  {len(new_rows)} new unlabeled rows to {dataset}")
    if dupes:
        print(f"Skipped {dupes} exact duplicates already in the dataset")


if __name__ == "__main__":
    main()
