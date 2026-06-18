# sources/sync-backup/borg/.github/workflows/black.yaml Research

## Purpose

`black.yaml` runs Black formatting checks for Python-related changes. It is a focused lint workflow separate from the broader CI workflow.

## Important APIs, Types, and Functions

The workflow triggers on pushes and pull requests touching `**.py`, `pyproject.toml`, or itself. It uses concurrency cancellation for pull requests, runs one `lint` job on `ubuntu-24.04`, checks out with `actions/checkout@v6`, and runs `psf/black` pinned to commit `87928e6d6761a4a6d22250e1fee5601b3998086e` with `version: "~= 24.0"`.

## Control Flow

GitHub path filters decide whether the workflow starts. The Black action installs/runs the requested Black version and fails the job if formatting differs.

## State and Persistence Behavior

The workflow does not commit formatting changes; it only reports pass/fail status. Concurrency can cancel older PR runs.

## Dependencies and Integration Points

It integrates with GitHub Actions, Black, Python source files, and `pyproject.toml` formatting settings. The comment notes that the workflow version should match local requirements in `requirements.d/codestyle.txt`.

## Risks and Edge Cases

The action is pinned by SHA, which is good for supply-chain stability, but the Black version range can still resolve to newer 24.x releases. If local pre-commit uses a different Black version, contributors can see mismatches. Path filters exclude non-Python generated formatting contexts.

## Test Signals

Signals are PR status checks and intentionally misformatted Python fixture changes. Compare workflow Black version against pre-commit and requirement pins during dependency updates.
