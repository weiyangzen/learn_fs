<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate11.py

Purpose: Ensures checkpoint does not read many pages deleted by a fast-truncate that is not visible to that checkpoint.

Important APIs/types/functions: Uses `checkpoint_thread`, `threading.Event`, `timing_stress_for_test=[checkpoint_slow]`, statistics `stat.conn.checkpoint_state` and `stat.conn.cache_read_deleted`, and `session.truncate`.

Control flow: The test creates an 80,000-row small-page table, reopens, sets oldest/stable to 100, writes a few timestamp-120 updates, starts a checkpoint thread, waits until checkpoint begins, then truncates keys 20,000-40,000 at timestamp 150 and commits. After joining the checkpoint thread, it asserts `cache_read_deleted` is less than 10.

State and persistence behavior: The checkpoint is intentionally concurrent with a later fast-truncate. Deleted pages should not be pulled into cache unnecessarily by a checkpoint that cannot see the truncate.

Dependencies and integration points: Integrates checkpoint concurrency, timing stress, statistics, fast-delete visibility, and thread cleanup. Tiered hook is skipped because regular checkpoint timing matters.

Risks: Race sensitivity is controlled by checkpoint state polling, but timing-based tests can still be environment-sensitive. Excessive deleted-page reads indicate performance and cache pressure regressions.

Test signals: `cache_read_deleted < 10` after concurrent checkpoint and truncate.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate11.py -->
