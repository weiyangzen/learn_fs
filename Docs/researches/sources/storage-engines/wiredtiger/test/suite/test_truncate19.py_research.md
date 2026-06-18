<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate19.py

Purpose: Mimics MongoDB oplog truncation workload and verifies repeated fast-truncate plus append cycles do not leave excessive disk usage.

Important APIs/types/functions: `test_truncate19` uses `SimpleDataSet`, helper `append_rows`, helper `do_truncate` with a high cursor and no low cursor, `stat.conn.rec_page_delete_fast`, checkpoints from another session, `os.path.getsize`, and `suite_random` import though not used. It skips tiered and disaggregated hooks because object file sizes are central to the assertion.

Control flow: The test creates an `oplog` table with one million rows and a dummy table, checkpoints, reopens, then loops 49 times. Each iteration starts a long-running transaction in a third session to keep truncate from becoming globally visible, truncates the oldest 10,000 rows from the main session, verifies fast-delete count, checkpoints, asserts `oplog.wt` is under 600MB, rolls back the long transaction, appends 10,000 rows at the tail, and advances start/end counters. A final checkpoint repeats the size assertion.

State and persistence behavior: The workload repeatedly creates and checkpoints fast-delete metadata while a long-running transaction affects global visibility, then appends new rows to keep logical size steady.

Dependencies and integration points: Integrates fast-delete, checkpoint cleanup, file block reuse/freeing, long-running transaction visibility, and real WT file sizing.

Risks: File-size thresholds can be platform/storage-layout sensitive, so tiered/disagg are skipped. The million-row setup is expensive but necessary to model oplog behavior.

Test signals: Positive fast-delete stats in every iteration and `oplog.wt` remaining below 600,000,000 bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate19.py -->
