# sources/storage-engines/pebble/scripts/run-crossversion-meta.sh

## Purpose
This script builds metamorphic test binaries for provided branches and runs the crossversion metamorphic test across those versions.

## Important APIs, Types, and Functions
It records the current branch, creates a temp directory, iterates branch arguments, checks out each branch, derives a version label, optionally selects a Go toolchain for version `24.1`, builds `./internal/metamorphic` test binaries, then runs `./internal/metamorphic/crossversion` with accumulated `-version` flags.

## Control Flow
After building binaries for all branches, it checks out the original branch and either runs `go test` directly or wraps it in `stress -p 1` when `STRESS` is set. Runtime parameters come from `TIMEOUT`, `SEED`, and `FACTOR` environment variables. The temp directory is removed after the run.

## State and Persistence Behavior
The script mutates git checkout state and writes temporary binaries. Test artifacts are written to `./artifacts`.

## Dependencies and Integration Points
It depends on git, Go, optional Go toolchain selection through `GOTOOLCHAIN`, optional `stress`, and the crossversion metamorphic test package.

## Risks
There is no cleanup trap, so failures before the final `rm -rf` can leave temp files or the repo on a different branch. It uses a Bash array assignment style with backticks that works but is unusual. Dirty worktrees are not checked, so branch checkout can fail or disturb user state.

## Test Signals
Success is a passing `TestMetaCrossVersion` run over all provided branch binaries, optionally under stress. Artifacts in `./artifacts` capture failure details.
