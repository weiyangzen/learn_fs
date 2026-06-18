# sources/storage-engines/wiredtiger/test/suite/test_txn06.py

## Purpose
`test_txn06.py` verifies long-running snapshots pin transaction state and produce the expected verbose diagnostic output while concurrent inserts allocate new transaction IDs.

## Important APIs, Types, and Functions
The class defines `test_long_running` with row and column scenarios. It uses `SimpleDataSet`, a source table and destination table, two sessions, verbose transaction logging, `captureout.checkAdditionalPattern`, and `ignoreStdoutPattern`.

## Control Flow
The test populates a large source table, opens a cursor in the main session to scan it, creates a destination table, and writes each source row into the destination through a second session. The source scan keeps a snapshot pinned while many inserts advance transaction state.

## State and Persistence Behavior
Persistent table data is incidental; the important state is in-memory transaction ID pinning caused by an active cursor/session snapshot.

## Dependencies and Integration Points
Depends on the capture-output test harness, `SimpleDataSet`, and WiredTiger verbose transaction diagnostics.

## Risks and Edge Cases
The signal is diagnostic-output based and may be sensitive to logging wording or background timing. It also writes 100,000 rows.

## Test Signals
The test requires an output pattern containing "pinned in session" and ignores trailing occurrences during teardown.
