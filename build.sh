#!/bin/sh
# Draw the front page, then copy it to the grader's output directory.
set -eu
here=$(dirname "$0")
python3 "$here/build_image.py"
python3 "$here/main.py"
