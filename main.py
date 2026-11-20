#!/usr/bin/env python3
"""Write the entry image to the grader's output directory.

The image itself is produced by build_image.py and shipped in this
repository as entry.png. This entrypoint uses only the standard library:
it reads the shipped PNG and writes it out again, byte for byte, so
running it twice always produces the same file.
"""
import os
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"


def write_entry() -> int:
    destination_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "entry.png"
    payload = SOURCE.read_bytes()
    destination.write_bytes(payload)
    print(f"wrote {destination} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(write_entry())
