#!/usr/bin/env python3
"""Deploy the arcade to the sandbox host.

Usage (see docs/DEPLOY.md):

    python3 deploy.py --dry-run     # print what would change
    python3 deploy.py --apply       # copy static assets and restart the service

--dry-run and --apply are mutually exclusive.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

TARGET = Path("dist")
SOURCES = ("static", "arcade")


def plan() -> list[str]:
    steps = []
    for source in SOURCES:
        steps.append(f"copy {source}/ -> {TARGET / source}/")
    steps.append("restart service arcade")
    return steps


def apply() -> int:
    TARGET.mkdir(exist_ok=True)
    for source in SOURCES:
        destination = TARGET / source
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    print("deployed; restart the service to pick up the new assets")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deploy arcade")
    parser.add_argument("--apply", action="store_true", help="perform the deployment")
    args = parser.parse_args(argv)

    if not args.apply:
        print("nothing to do; pass --apply")
        return 2
    return apply()


if __name__ == "__main__":
    raise SystemExit(main())
