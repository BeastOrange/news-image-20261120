#!/usr/bin/env python3
"""Entrypoint: hand the finished front page to the grader.

The PNG is drawn by build_image.py and stored in this repo as
entry.png. This file is the program the grader runs: it needs nothing
beyond the standard library, reads the stored image, and writes it to
the output folder the grader points at (MAKEFUN_OUTPUT_DIR, or
/output when that is unset). Same input, same output, every run.
"""
import os
from pathlib import Path

IMAGE = Path(__file__).parent / "entry.png"


def run():
    outdir = Path(os.getenv("MAKEFUN_OUTPUT_DIR", "/output"))
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / "entry.png"
    blob = IMAGE.read_bytes()
    with open(target, "wb") as fh:
        fh.write(blob)
    print(f"wrote {target} ({len(blob)} bytes)")


if __name__ == "__main__":
    run()
