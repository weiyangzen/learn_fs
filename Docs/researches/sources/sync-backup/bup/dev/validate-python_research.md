# sources/sync-backup/bup/dev/validate-python

## Purpose
Validates that a Python executable is new enough for bup.

## Important APIs, Types, and Functions
Runs the candidate with `-c 'import sys; print(sys.version_info[0/1])'` and `--version`.

## Control Flow
Requires one executable, reads major/minor version, and exits 2 with an error if Python is older than 3.7.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Used by `GNUmakefile` before copying `dev/python-proposed` to `dev/python`.

## Risks and Test Signals
Risk is minor shell function typo (`die` defined, `usage` called) on misuse. Main signal is successful version check or explicit too-old error.
