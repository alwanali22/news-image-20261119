"""Entry program for news-image-20261119 v2 (19 November 2026).

v2: 43 stories — trilateral result, Anthropic IPO debut, GTA VI launch day.
See V2-RESEARCH-2026-11-20.md for the verified research log.

Copies the pre-rendered entry.png from this repository to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), byte for byte, then
verifies the copy matches the repository file exactly.
Standard library only, no network, fully deterministic: two runs write
the same bytes, because the file copied is fixed at this commit.
"""

import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    with open(src, "rb") as f:
        want = f.read()
    with open(dst, "rb") as f:
        got = f.read()
    if got != want:
        raise RuntimeError("output does not match entry.png")
    print("wrote %s (%d bytes, verified)" % (dst, len(got)))


if __name__ == "__main__":
    main()
