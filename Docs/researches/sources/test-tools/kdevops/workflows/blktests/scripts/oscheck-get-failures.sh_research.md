# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-get-failures.sh

## Purpose
Prints the effective blktests failure/expunge list for the current OS, kernel, and optional test group.

## Important APIs, Types, and Functions
Local functions are `oscheck_fail_usage()` and `parse_args()`. It relies on `oscheck-lib.sh` functions for initialization, OS/kernel verification, group selection, expunge construction, and temp-file creation.

## Control Flow
The script sources `oscheck-lib.sh`, parses `--test-group`/`--help`, reads OS metadata, validates/infer the run group, computes expunges, writes expunge test IDs to a temp file, sorts/deduplicates output, prints it, and removes the temp file.

## State and Persistence Behavior
Creates a temporary file and deletes it. Reads OS release data, distro helper files, expunge files, result directories, and blktests `tests/`.

## Dependencies and Integration Points
Must run in the kdevops blktests script layout with bash, awk, sed, sort, uniq, readlink, and the shared oscheck library.

## Risks and Edge Cases
Missing value after `--test-group` is not checked. Temp cleanup has no trap. Library duplicate detection is substring-based.

## Test Signals
Run help, valid/invalid groups, no expunges, kernel-specific expunges, distro-version expunges, and missing library cases. Confirm output is sorted and unique.
