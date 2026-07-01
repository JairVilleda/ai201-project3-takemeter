#!/usr/bin/env python3
"""
TakeMeter — manual annotation tool for Milestone 3 (r/worldcup dataset).

Labels are fixed by planning.md and MUST NOT be changed:
    Analysis   — explains a claim with evidence/reasoning/stats/observation
    Prediction — primary purpose is forecasting a future outcome
    Reaction   — emotional response/opinion without substantial reasoning

Decision rule for the Analysis/Prediction edge case:
    If the main claim is future-oriented -> Prediction (even with evidence).
    If it explains why/what is -> Analysis.

planning.md forbids LLM labeling of the final dataset: every label here is
assigned by you, manually.

Usage:
    python3 annotate.py                 # annotate worldcup_dataset.csv
    python3 annotate.py --report        # print the balance/summary report only
    python3 annotate.py --file my.csv   # use a different CSV
"""

import argparse
import csv
import os
import sys
import tempfile

# --- Fixed taxonomy (do not edit — defined in planning.md) -------------------
LABELS = {
    "a": "Analysis",
    "p": "Prediction",
    "r": "Reaction",
}
VALID_LABELS = set(LABELS.values())
COLUMNS = ["text", "label", "notes"]

# Distribution rules from planning.md
MAX_SHARE = 0.70   # no single label may exceed 70%
MIN_SHARE = 0.20   # no single label should fall below 20%
TARGET_TOTAL = 200


# --- CSV I/O -----------------------------------------------------------------
def load_rows(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        print("Create it with a header row: text,label,notes")
        sys.exit(1)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            print(f"CSV is missing required columns: {missing}")
            print(f"Expected header: {','.join(COLUMNS)}")
            sys.exit(1)
        rows = []
        for r in reader:
            rows.append({c: (r.get(c) or "").strip() for c in COLUMNS})
    return rows


def save_rows(path, rows):
    """Atomic write: write to a temp file in the same dir, then replace."""
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            for r in rows:
                writer.writerow({c: r.get(c, "") for c in COLUMNS})
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# --- Stats / reporting -------------------------------------------------------
def counts(rows):
    c = {lbl: 0 for lbl in VALID_LABELS}
    unlabeled = 0
    other = {}
    for r in rows:
        lbl = r["label"]
        if not lbl:
            unlabeled += 1
        elif lbl in VALID_LABELS:
            c[lbl] += 1
        else:
            other[lbl] = other.get(lbl, 0) + 1
    return c, unlabeled, other


def print_stats(rows):
    c, unlabeled, other = counts(rows)
    total = len(rows)
    labeled = sum(c.values()) + sum(other.values())
    print("\n" + "=" * 52)
    print(f"  Rows in file : {total}")
    print(f"  Labeled      : {labeled}")
    print(f"  Unlabeled    : {unlabeled}")
    print("-" * 52)
    if labeled:
        for lbl in sorted(VALID_LABELS):
            n = c[lbl]
            pct = 100 * n / labeled
            flag = ""
            if pct > MAX_SHARE * 100:
                flag = "  <-- OVER 70% (rule violation)"
            elif pct < MIN_SHARE * 100:
                flag = "  <-- under 20% (collect more)"
            print(f"  {lbl:<11}: {n:>4}  ({pct:5.1f}% of labeled){flag}")
    if other:
        print("-" * 52)
        print("  INVALID labels found (fix these — not in taxonomy):")
        for lbl, n in sorted(other.items()):
            print(f"    {lbl!r}: {n}")
    print("=" * 52)
    if labeled < TARGET_TOTAL:
        print(f"  Need {TARGET_TOTAL - labeled} more labeled examples "
              f"to reach the {TARGET_TOTAL}-example target.")
    print()


def print_report(rows):
    print_stats(rows)
    # Difficult cases = any labeled row that carries an annotation note.
    difficult = [r for r in rows if r["notes"] and r["label"]]
    print(f"Difficult / noted cases: {len(difficult)}")
    print("-" * 52)
    for i, r in enumerate(difficult, 1):
        text = r["text"]
        preview = (text[:90] + "...") if len(text) > 90 else text
        print(f"{i}. [{r['label']}] {preview}")
        print(f"    note: {r['notes']}")
    print()


# --- Annotation loop ---------------------------------------------------------
HELP = """
Commands:
  a            label as Analysis
  p            label as Prediction
  r            label as Reaction
  s            skip (leave unlabeled, go to next)
  b            go back to the previous example
  c            show current counts / percentages
  ?            show this help
  q            save and quit
After choosing a label you'll be asked for an optional note (Enter = none).
"""


def annotate(path):
    rows = load_rows(path)
    print(f"Loaded {len(rows)} rows from {path}")
    print("Labels (fixed): Analysis (a) | Prediction (p) | Reaction (r)")
    print(HELP)
    print_stats(rows)

    # Work queue = indices of currently unlabeled rows (resume-friendly).
    queue = [i for i, r in enumerate(rows) if not rows[i]["label"]]
    if not queue:
        print("Nothing to annotate — every row already has a label.")
        print_report(rows)
        return

    pos = 0
    history = []  # stack of queue positions we've labeled, for 'back'
    while pos < len(queue):
        idx = queue[pos]
        row = rows[idx]
        done = pos
        remaining = len(queue) - pos
        print("\n" + "#" * 52)
        print(f"  Example {idx + 1} (file row)  |  {remaining} unlabeled left")
        print("#" * 52)
        print(row["text"])
        print("-" * 52)
        choice = input("Label [a/p/r] (s/b/c/?/q): ").strip().lower()

        if choice == "q":
            break
        if choice == "?":
            print(HELP)
            continue
        if choice == "c":
            print_stats(rows)
            continue
        if choice == "s":
            pos += 1
            continue
        if choice == "b":
            if history:
                pos = history.pop()
            else:
                print("Already at the first example.")
            continue
        if choice not in LABELS:
            print("Unrecognized command. Type ? for help.")
            continue

        label = LABELS[choice]
        note = input("Optional note (Enter to skip): ").strip()
        row["label"] = label
        row["notes"] = note
        save_rows(path, rows)  # save after every annotation
        print(f"  -> saved as {label}" + (f"  (note recorded)" if note else ""))
        history.append(pos)
        pos += 1

    print("\nStopping. Progress saved.")
    print_report(rows)


def main():
    ap = argparse.ArgumentParser(description="TakeMeter manual annotation tool")
    ap.add_argument("--file", default="worldcup_dataset.csv",
                    help="CSV to annotate (default: worldcup_dataset.csv)")
    ap.add_argument("--report", action="store_true",
                    help="Print the balance/summary report and exit")
    args = ap.parse_args()

    if args.report:
        print_report(load_rows(args.file))
        return
    annotate(args.file)


if __name__ == "__main__":
    main()
