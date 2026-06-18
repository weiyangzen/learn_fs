# sources/storage-engines/wiredtiger/test/suite/test_checkpoint24.py

Purpose: non-timestamped fast-delete checkpoint test. It verifies checkpoint cursors can read a checkpoint containing pages deleted through fast truncate, including after optional reopen for named checkpoints.

Important APIs and types: `session.truncate`, `stat.conn.rec_page_delete_fast`, `SimpleDataSet`, named/unnamed checkpoint helper, and `session.open_cursor(..., checkpoint=...)`.

Control flow: populate a table, reopen to force data on disk, truncate the middle half, assert fast-delete stats increased, checkpoint, optionally reopen, then scan the checkpoint cursor.

State and persistence behavior: the checkpoint stores fast-deleted page state, and the cursor must enumerate only surviving records. Reopen coverage verifies named checkpoint metadata remains usable after restart.

Dependencies and integration points: uses row and column store scenarios, statistics cursor, and checkpoint cursor reads. Unnamed checkpoint plus reopen is intentionally avoided because reopen creates a new unnamed checkpoint.

Risks: depends on truncate choosing fast-delete for at least one page; page size or dataset changes may reduce coverage. Skipped on tiered/disaggregated hooks.

Test signals: `rec_page_delete_fast` is greater than zero and the checkpoint scan returns exactly half the original rows with the original value.
