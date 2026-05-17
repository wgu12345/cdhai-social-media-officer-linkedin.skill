#!/usr/bin/env python3
"""
reviewer_check.py — v0.4.3

Hard contract gate. Runs AT THE START of Phase 9 (output assembly),
before build_docx writes linkedin_post.docx.

Confirms that the reviewer sub-agent actually ran by checking for a flag
file in the cache. SKILL.md says reviewer is mandatory; this script
enforces it mechanically.

Exits 0  → reviewer ran, build_docx may proceed.
Exits 2  → no reviewer flag found, output assembly MUST stop.

Usage:
    python3 _helpers/reviewer_check.py <run_id>

The writer skill writes the flag like this when the reviewer sub-agent
completes:
    touch ~/.cdhai-linkedin-skill/cache/reviewer_ran_<run_id>.flag
"""

import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".cdhai-linkedin-skill" / "cache"


def main():
    if len(sys.argv) < 2:
        print("Usage: reviewer_check.py <run_id>", file=sys.stderr)
        sys.exit(3)

    run_id = sys.argv[1]
    flag = CACHE_DIR / f"reviewer_ran_{run_id}.flag"

    if not flag.exists():
        print(
            f"BLOCKED: Reviewer sub-agent did not run for run_id={run_id}.\n"
            "\n"
            f"Expected flag file: {flag}\n"
            "\n"
            "Phase 8 of this skill is mandatory and runs as an independent "
            "Codex sub-agent. The writer agent may NOT perform self-review "
            "in the same turn — that bypasses the fresh-context requirement "
            "that the 9 quality checks depend on.\n"
            "\n"
            "If you are Codex: spawn the reviewer sub-agent now, then write "
            f"the flag file ({flag}) when it completes, then re-run this "
            "check.\n"
            "\n"
            "If you are the user and Codex is refusing to spawn a sub-agent: "
            "this likely means your Codex App config disabled sub-agents. "
            "Re-enable sub-agents and run the skill again.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"OK: reviewer ran for run_id={run_id}")
    sys.exit(0)


if __name__ == "__main__":
    main()
