# sources/storage-engines/wiredtiger/test/suite/test_util07.py

## Purpose
`test_util07.py` validates `wt read` for missing and present string keys, including behavior across explicit connection close/open helper paths.

## Important APIs, Types, and Functions
The class defines `populate`, `close_conn`, `open_conn`, `test_read_empty`, and `test_read_populated`. It uses `runWt(['read', ...])`, output/error files, and file-content check helpers.

## Control Flow
The empty-table test creates a table and runs `wt read` for `NoMatch`, expecting command failure, empty stdout, and "not found" stderr. The populated test inserts uppercase `KEYnn` values, reads `KEY49` successfully, then reads lowercase `key49` and expects not found.

## State and Persistence Behavior
The table contains simple string key/value records. Persistence is accessed through the external `wt` utility after connection lifecycle changes.

## Dependencies and Integration Points
Depends on `suite_subprocess`, external `wt read`, and test harness output-file assertions.

## Risks and Edge Cases
Case sensitivity is an explicit edge: `KEY49` succeeds and `key49` fails.

## Test Signals
Expected stdout/stderr contents and process success/failure states are verified.
