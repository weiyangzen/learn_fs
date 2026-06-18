# sources/storage-engines/wiredtiger/test/suite/test_truncate23.py

## Purpose
`test_truncate23.py` exercises truncate boundary behavior with and without prepared transactions, especially records inserted on, outside, and adjacent to truncate bounds.

## Important APIs, Types, and Functions
The class defines `in_range`, `scenario`, and `test_truncate23`. It uses `session.create`, `session.truncate` with URI/start/stop combinations, prepared transaction APIs (`prepare_transaction`, timestamped commit/durable timestamps), and a helper `scenario_num` to generate separate table URIs.

## Control Flow
Each scenario creates a no-logging table, inserts committed boundary records, optionally runs a second prepared transaction inserting the same set, truncates a selected range, commits the truncate, commits the prepared writer if enabled, then scans and compares expected keys and values.

## State and Persistence Behavior
The table is ephemeral test state, but it models timestamped prepared updates interacting with truncate-generated deletes. Values for keys outside the truncated range must persist; values inside the range must be removed or masked according to commit ordering.

## Dependencies and Integration Points
Depends on WiredTiger's prepared transaction protocol, unsigned integer key/value table format, and truncate cursor boundary rules.

## Risks and Edge Cases
The file explicitly covers start-only, stop-only, both-bound, and full-object truncates, plus exact-bound and adjacent-key cases. The test is currently skipped for `FIXME-WT-13232`, making it a known-risk coverage placeholder.

## Test Signals
When enabled, the full cursor scan must match the computed `expect` dictionary for each generated scenario.
