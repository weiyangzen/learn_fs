<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py

## Purpose
Checks required command-line dependencies before benchmark execution.

## Important APIs, Types, And Functions
`check_dependencies(packages, log)` loops over package names, logs the check, runs `<package> --version`, logs an error and opens `bash` on failure.

## Control Flow
`check_dependencies(packages, log)` loops over package names, logs the check, runs `<package> --version`, logs an error and opens `bash` on failure.

## State And Persistence Behavior
No persistent state, but failed checks can leave the process in an interactive shell.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Used by rename and listing benchmarks before invoking `gcloud`, `gsutil`, or `gcsfuse`.

## Risks And Edge Cases
Opening `bash` is unsuitable for noninteractive automation and does not raise a Python exception.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py -->
