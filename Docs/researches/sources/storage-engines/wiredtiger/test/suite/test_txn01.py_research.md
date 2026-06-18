# sources/storage-engines/wiredtiger/test/suite/test_txn01.py

## Purpose
`test_txn01.py` covers basic transaction visibility across row/column and file/table object types, and verifies that read-committed is the default isolation level.

## Important APIs, Types, and Functions
It defines `test_txn01` with helpers `cursor_count`, `check_checkpoint`, `check_txn_cursor`, `check_txn_session`, `check`, and `test_visibility`, plus `test_read_committed_default`. It uses `make_scenarios`, transaction begin/commit, checkpoints, and isolation strings.

## Control Flow
`test_visibility` creates a dataset, inserts 1,000 records inside a transaction, periodically checks that the current cursor and read-uncommitted readers see uncommitted rows while snapshot/read-committed and checkpoints see only committed rows, then commits all rows and rechecks. The default-isolation test creates one uncommitted row and verifies a separate reader does not see it.

## State and Persistence Behavior
Checkpoints provide persisted visibility assertions; transactional changes remain isolated until commit. Column-store phantom handling filters only rows with the test value.

## Dependencies and Integration Points
Depends on WiredTiger isolation levels, checkpoint cursors, and scenario generation.

## Risks and Edge Cases
Column-store append phantoms require special counting. Any default isolation change would break the second class.

## Test Signals
Counts for current, read-uncommitted, snapshot, read-committed, and checkpoint readers must match expected committed/total values.
