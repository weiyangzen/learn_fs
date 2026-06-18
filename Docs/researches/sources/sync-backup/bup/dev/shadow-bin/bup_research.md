# sources/sync-backup/bup/dev/shadow-bin/bup

## Purpose
Intentional failing `bup` executable placed early in `PATH` to catch tests or build steps that accidentally invoke an installed/local `bup` instead of repository wrappers.

## Important APIs, Types, and Functions
Shell script prints a fixed error message and exits 2.

## Control Flow
Always fails.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Prepended to `PATH` by `GNUmakefile`; `run_check` asserts `command -v bup` points here while `./bup` is used explicitly.

## Risks and Test Signals
Signal is intentional failure on accidental `bup version`. Risk is scripts that legitimately need `bup` by PATH must override path intentionally.
