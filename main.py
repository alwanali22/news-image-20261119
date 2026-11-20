"""Publish the pre-rendered front page for news-image-20261119 v2.

v2-rewrite: 43 stories — trilateral result, Anthropic IPO debut,
GTA VI launch day. See V2-RESEARCH-2026-11-20.md for the verified log.

The entry image is drawn ahead of time by draw_v2.py and stored in
this repository as entry.png. This program only moves it into the
directory the harness reads from, then proves the delivered file is
an exact copy by comparing SHA-256 digests.

Pure standard library. No network, no clock, no randomness: the same
repository always delivers the same bytes.
"""

import hashlib
import os
from pathlib import Path


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def deliver():
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    dest_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / "entry.png"
    target.write_bytes(source.read_bytes())
    if _digest(target) != _digest(source):
        raise RuntimeError("delivered file differs from entry.png")
    print("delivered %s (%d bytes, sha256 %s)"
          % (target, target.stat().st_size, _digest(target)))


if __name__ == "__main__":
    deliver()
