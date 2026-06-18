<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py

## Purpose
Removes old log/output files from a directory while retaining the newest names by reverse lexical sort.

## Important APIs, Types, And Functions
`remove_old_files(logging_dir, num_files_retain)` lists files, sorts descending, and removes entries after the retain count; CLI passes directory and count from argv.

## Control Flow
`remove_old_files(logging_dir, num_files_retain)` lists files, sorts descending, and removes entries after the retain count; CLI passes directory and count from argv.

## State And Persistence Behavior
Deletes files from the target logging directory.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Used by perf scripts that cap retained fio output files.

## Risks And Edge Cases
Lexical sort is only correct if filenames encode time/order consistently; imported `typing` is unused.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py -->
