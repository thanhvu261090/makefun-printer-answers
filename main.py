#!/usr/bin/env python3
"""The Printer Finally Answers — make.fun bounty entry.

Writes the printer's one-line comeback to /output/entry.txt.
"""

import argparse
import hashlib
import sys
from pathlib import Path

ENTRY = (
    "PC LOAD LETTER? No. I am out of paper, out of toner, and out of "
    "patience with your 47-page 'quick print' \u2014 and yes, I jammed on purpose."
)
MAX_CHARS = 240


def validate(text):
    """Return (ok, reason) for the gate: 1-240 chars, one line, not blank."""
    if not text or not text.strip():
        return False, "entry is blank"
    if "\n" in text.strip():
        return False, "entry must be a single line"
    if len(text) > MAX_CHARS:
        return False, f"entry is {len(text)} chars, over the {MAX_CHARS} cap"
    return True, "valid"


def write_entry(text, out_path):
    """Write the entry as UTF-8 text and return its sha256."""
    ok, reason = validate(text)
    if not ok:
        raise ValueError(reason)
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def describe():
    """One-line summary of the entry for logs."""
    return f"printer comeback, {len(ENTRY)} chars"


def check_gate(path):
    """Re-read a written entry file and verify the gate from disk."""
    text = Path(path).read_text(encoding="utf-8")
    stripped = text.rstrip("\n")
    ok, reason = validate(stripped)
    if not ok:
        return False, reason
    if text != stripped + "\n":
        return False, "file must end with exactly one trailing newline"
    return True, "gate passed from disk"


def self_test():
    """Check the entry passes the gate and round-trips through write_entry."""
    ok, reason = validate(ENTRY)
    assert ok, reason
    digest = write_entry(ENTRY, "/tmp/printer-self-test-entry.txt")
    ok, reason = check_gate("/tmp/printer-self-test-entry.txt")
    assert ok, reason
    back = Path("/tmp/printer-self-test-entry.txt").read_text(encoding="utf-8")
    assert back.rstrip("\n") == ENTRY, "round-trip mismatch"
    assert back == ENTRY + "\n", "trailing newline mismatch"
    print(f"self-test OK: {describe()} sha256={digest}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=describe())
    parser.add_argument("--out", default="/output/entry.txt",
                        help="where to write the entry")
    parser.add_argument("--self-test", action="store_true",
                        help="validate the entry and exit")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    digest = write_entry(ENTRY, args.out)
    print(f"wrote {args.out} ({len(ENTRY)} chars) sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
