# sources/storage-engines/wiredtiger/test/suite/test_util14.py

## Purpose

`test_util14.py` tests the `wt truncate` command on a populated table and validates common error paths for missing, invalid, nonexistent, and duplicate URI arguments.

## Important APIs, Types, and Functions

`test_util14` has one method, `test_truncate_process`, using `session.create`, table existence checks, cursor inserts, `runWt`, `check_empty_file`, and `check_file_contains`.

## Control Flow

The test creates a table, inserts 1000 string rows, invokes `wt truncate table:<name>`, then uses `wt read` to confirm the table still exists but has no matching records. It then runs malformed truncate commands and checks stderr.

## State and Persistence Behavior

The table remains as metadata after truncate while its records are removed. Output and error files are reused for positive and negative command checks.

## Dependencies and Integration Points

Depends on `suite_subprocess`, `wt truncate`, `wt read`, WiredTiger table metadata, and row-store cursor behavior.

## Risks and Edge Cases

Exact error messages (`usage:`, `No such file or directory`, `not found`) are part of the assertion surface. The test only covers full-object truncation, not bounded cursor/key truncation.

## Test Signals

Strong signals are table existence after truncate, empty read stdout, expected not-found stderr for reads, and clear failure behavior for invalid truncate invocations.
