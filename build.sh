#!/bin/sh
# Rebuild the front page and hand it to the grader's output folder.
set -eu
cd "$(dirname "$0")"
python3 build_image.py
python3 main.py
