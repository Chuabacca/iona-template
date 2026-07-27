#!/usr/bin/env python3
"""tsk_convert — one-time converter: cross-reference dump -> iona key grammar.

Usage: scripts/tsk_convert.py <cross_references.txt> [--min-votes 3] [--top 10]
Input: openbible.info cross-reference TSV (CC-BY): From<TAB>To<TAB>Votes.
Output: scripts/tsk/cross_references.json — {"GEN.1.1": [["PRO.8.22-30", 59], …]},
refs sorted by votes desc, top N per source verse. Rows that fail validation
against scripts/books.json are dropped loudly (counted, reported).
Exit 0 on success, 1 on errors.
"""

import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

OUT_PATH = os.path.join(lib.ROOT, "scripts", "tsk", "cross_references.json")


def to_key(ref):
    """'Gen.1.1' -> 'GEN.1.1' (validated). Raises SpecError."""
    _, alias = lib.load_books()
    parts = ref.split(".")
    if len(parts) != 3:
        raise lib.SpecError("unexpected ref %r" % ref)
    book, ch, v = parts
    code = alias.get(book.lower())
    if code is None:
        raise lib.SpecError("unknown book %r" % book)
    if int(v) == 0:
        raise lib.SpecError("verse 0 (title verse) in %r" % ref)
    key = "%s.%d.%d" % (code, int(ch), int(v))
    lib.parse_key(key)
    return key


def to_target(ref):
    """Single ref or 'A-B' span -> display key (validated where possible)."""
    if "-" in ref:
        a, b = ref.split("-", 1)
        ka, kb = to_key(a), to_key(b)
        pa, pb = lib.parse_key(ka), lib.parse_key(kb)
        if pa["book"] == pb["book"] and pa["ch"] == pb["ch"]:
            key = "%s.%d.%d-%d" % (pa["book"], pa["ch"], pa["v1"], pb["v1"])
            lib.parse_key(key)
            return key
        return "%s..%s" % (ka, kb)  # cross-chapter span, display-only
    return to_key(ref)


def main(argv):
    if not argv or "--help" in argv:
        print(__doc__)
        return 0 if "--help" in argv else 1
    min_votes, top = 3, 10
    if "--min-votes" in argv:
        i = argv.index("--min-votes")
        min_votes = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if "--top" in argv:
        i = argv.index("--top")
        top = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    src = argv[0]
    if not os.path.exists(src):
        print("ERROR: input not found: %s" % src, file=sys.stderr)
        return 1
    refs = defaultdict(list)
    dropped, kept = 0, 0
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("From Verse"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                dropped += 1
                continue
            try:
                votes = int(parts[2])
                if votes < min_votes:
                    continue
                frm = to_key(parts[0])
                tgt = to_target(parts[1])
            except (lib.SpecError, ValueError):
                dropped += 1
                continue
            refs[frm].append((tgt, votes))
            kept += 1
    out = {}
    for frm in sorted(refs):
        ranked = sorted(refs[frm], key=lambda t: (-t[1], t[0]))[:top]
        out[frm] = [[t, v] for t, v in ranked]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), sort_keys=True)
    print("tsk_convert: %d refs kept (votes>=%d, top %d/verse), %d dropped, "
          "%d source verses -> %s"
          % (kept, min_votes, top, dropped, len(out),
             os.path.relpath(OUT_PATH, lib.ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
