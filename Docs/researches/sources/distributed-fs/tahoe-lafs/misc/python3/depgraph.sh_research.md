# sources/distributed-fs/tahoe-lafs/misc/python3/depgraph.sh

## Purpose

This CI shell script builds and publishes Tahoe dependency graph JSON files to the `gh-pages` branch of `tahoe-lafs/tahoe-depgraph`.

## Important APIs, Types, and Functions

It uses `git clone -b gh-pages`, runs `misc/python3/tahoe-depgraph.py`, checks `git diff-index --quiet HEAD`, configures a bot identity, commits `tahoe-deps.json` and `tahoe-ported.json`, and pushes only on CircleCI `master`.

## Control Flow

With `set -x` and `set -eo pipefail`, it clones the publishing repo, generates data from the current Tahoe checkout, exits without commit if unchanged, commits with source repo/SHA in the message, refuses to push on non-master branches, and pushes to `gh-pages` on master.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is a cloned `tahoe-depgraph` directory and possibly a pushed commit. Dependencies are Git, CircleCI env vars, SSH credentials, and Python dependencies of `tahoe-depgraph.py`. Risks include fixed GitHub SSH target, no cleanup, publishing branch assumptions, and commit message depending on env vars. Tests should run in a temp repo with fake env vars and a mocked `git push`, verifying unchanged and changed cases.
