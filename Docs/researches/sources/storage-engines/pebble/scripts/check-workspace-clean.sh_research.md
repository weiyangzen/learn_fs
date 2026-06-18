# sources/storage-engines/pebble/scripts/check-workspace-clean.sh

## Purpose
This CI helper fails if the git workspace is dirty, typically after running generation commands.

## Important APIs, Types, and Functions
The script uses `set -euo pipefail`, `git status --porcelain`, `git status`, and `git diff --no-ext-diff -a`.

## Control Flow
It captures porcelain status including stderr. If non-empty, it prints status and diff to stderr, emits a generation-change error, and exits 1. Otherwise it exits successfully.

## State and Persistence Behavior
It does not mutate the workspace.

## Dependencies and Integration Points
It integrates with CI generation checks and any target that must prove generated files are committed.

## Risks
The error message is specific to `make generate`, even if another command dirtied the workspace. Capturing stderr into the condition means git command errors also cause failure.

## Test Signals
No direct tests are present; signal is CI failure with printed status and diff.
