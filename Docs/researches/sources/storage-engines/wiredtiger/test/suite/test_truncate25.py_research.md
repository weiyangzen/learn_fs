# sources/storage-engines/wiredtiger/test/suite/test_truncate25.py

## Purpose
`test_truncate25.py` verifies that a no-timestamp range truncate after stable checkpointing does not produce fast-delete pages and preserves timestamped visibility semantics.

## Important APIs, Types, and Functions
The class defines `uri`, `nrows`, and `test_truncate25`. It uses timestamped inserts at 30 and 50, `conn.set_timestamp`, `session.checkpoint`, `reopen_conn`, transactions with `no_timestamp=true`, `session.truncate`, `stat.conn.rec_page_delete_fast`, and read timestamp checks.

## Control Flow
Rows are first inserted at timestamp 30, updated at timestamp 50, stabilized and checkpointed, then the connection is reopened. A no-timestamp transaction truncates keys 1 through `nrows`, commits, stats are checked, one more timestamped update occurs at 60, stable is advanced, checkpoint/reopen happens again, and a read at timestamp 30 searches key 1.

## State and Persistence Behavior
The test combines stable checkpoints, non-timestamped deletes, and later timestamped updates. No-timestamp truncate should not fast-delete pages in this historical visibility situation.

## Dependencies and Integration Points
Depends on `SimpleDataSet`, WiredTiger statistics, timestamp APIs, and restart semantics.

## Risks and Edge Cases
Incorrect fast-delete optimization could discard historical values needed for timestamp reads or produce inconsistent replay after reopen.

## Test Signals
The key signal is `fastdelete_pages == 0`; final timestamped search verifies absence at the selected historical read point.
