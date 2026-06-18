<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py

## Purpose
Unit tests for log-retention deletion behavior.

## Important APIs, Types, And Functions
Creates temporary `fio_log_test/log_dir`, populates numbered files, calls `remove_old_files`, and asserts remaining names.

## Control Flow
Creates temporary `fio_log_test/log_dir`, populates numbered files, calls `remove_old_files`, and asserts remaining names.

## State And Persistence Behavior
Creates and removes a local test directory with `os.system`.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Covers fewer-than, zero, and more-than retention scenarios.

## Risks And Edge Cases
Uses shell `rm -r`/`touch`; tests rely on current working directory.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py -->
