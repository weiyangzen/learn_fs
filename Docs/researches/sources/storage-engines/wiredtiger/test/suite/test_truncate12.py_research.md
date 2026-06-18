<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate12.py

Purpose: Ensures transaction IDs on fast-truncate metadata remain valid after recovery, even when truncate information is loaded during rollback-to-stable and remains in cache.

Important APIs/types/functions: Uses `simulate_crash_restart`, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, `session.truncate`, named checkpoint `pointy`, timestamped transactions, and helper `check`.

Control flow: The test writes baseline rows in table 1 at timestamp 10 and stabilizes them, reopens, writes many timestamp-20 rows to table 2 to advance transaction IDs, fast-truncates most of table 1 at timestamp 30, updates retained rows at timestamp 40, advances stable to 35, checkpoints, crashes/restarts, and verifies retained/truncated data at timestamp 50 and in the named checkpoint.

State and persistence behavior: The test depends on fast-delete metadata written to disk and recovery-time RTS rolling back timestamp-40 updates while retaining timestamp-30 truncate. It also verifies deleted pages were not instantiated during recovery.

Dependencies and integration points: Integrates transaction ID visibility, fast-delete, RTS during crash recovery, named checkpoints, statistics, and row/column formats.

Risks: Mishandling write generation or transaction IDs can make truncates invisible after recovery. Instantiating deleted pages during recovery would show up as cache/stat regressions.

Test signals: Fast-delete count, `cache_read_deleted == 0`, and exact data checks in live and checkpoint cursors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate12.py -->
