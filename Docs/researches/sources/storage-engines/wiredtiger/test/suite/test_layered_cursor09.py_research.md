# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor09.py

Purpose: verifies cursor walking over checkpointed delta pages respects read timestamps and reconstructs updated values in both directions after reopen.

Important APIs/types/functions: uses data-source statistic `stat.dsrc.rec_page_delta_leaf`, timestamped transactions, stable timestamps, checkpoints, `reopen_conn`, read-timestamp transactions, and cursor `next`/`prev`.

Control flow: creates a layered table, inserts keys 1-99 mostly at timestamp 10, with key 50 at timestamp 20, sets stable 20 and checkpoints. It updates key 50 to `value2` at timestamp 30, sets stable 30, checkpoints, then asserts the data-source delta-page stat is greater than zero. After reopening, it reads at timestamp 30 and scans forward/backward expecting all 99 rows with key 50 as `value2`. It then reads at timestamp 10 and scans forward/backward expecting only timestamp-10 visible rows, count 98, all with original `value`.

State and persistence behavior: persistent checkpoint state includes a delta page from the update. Timestamp visibility excludes key 50 at timestamp 10 because it was inserted at timestamp 20.

Dependencies/integration points: delta reconciliation, timestamp visibility, reopen/recovery, forward/backward cursor traversal, and stats.

Risks: assumes workload generates at least one delta page. Cursor reuse across transactions depends on rollback/reset semantics from previous scans.

Test signals: pass means delta pages are generated and cursor walks reconstruct correct values/counts at different read timestamps.
