# sources/storage-engines/wiredtiger/test/suite/test_truncate24.py

## Purpose
`test_truncate24.py` validates full-table truncate visibility at timestamps, ensuring fast-delete pages are created while readers at an earlier timestamp still see pre-truncate values.

## Important APIs, Types, and Functions
The class uses row and column scenarios plus a timestamp/no-timestamp scenario set. It calls `session.truncate(uri, None, None, None)`, `timestamp_transaction`, timestamped commit, read timestamp transactions, `stat.conn.rec_page_delete_fast`, and `runningHook('disagg')` skip logic.

## Control Flow
The test populates a dataset, reopens, reads values, starts a transaction, timestamps the truncate at 10 when configured, truncates the whole URI, opens a second cursor before commit to verify old values are visible, commits at timestamp 20, verifies fast-delete stats, then reads at timestamp 10 and checks which keys are absent or visible.

## State and Persistence Behavior
It stresses timestamped truncate durability and snapshot reads. Full-table truncate creates page-level fast deletes but historical reads must retain correct older versions.

## Dependencies and Integration Points
Depends on WiredTiger timestamp machinery, connection statistics, `SimpleDataSet`, and disaggregated-storage hook behavior.

## Risks and Edge Cases
Column-store support differs under the disagg hook. Boundary risks include incorrect read timestamp visibility and fast-delete stats not incrementing after full-object truncate.

## Test Signals
Signals are successful pre-commit reads, `fastdelete_pages > 0`, and timestamped post-commit searches returning the expected found/not-found result.
