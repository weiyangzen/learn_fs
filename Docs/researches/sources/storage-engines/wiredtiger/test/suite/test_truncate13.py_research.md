<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate13.py

Purpose: Tests reading gaps created by fast-delete under unstable, stable, and globally visible timestamp states, optionally followed by new data.

Important APIs/types/functions: Uses `session.truncate`, `stat.conn.rec_page_delete_fast`, `debug=(release_evict)`, timestamped checks, and scenarios over range location, timestamp advancement, add/no-add, and key format.

Control flow: The test writes full-table value A at timestamp 20 and value B at timestamp 30, evicts pages, advances stable to 25, checkpoints, then fast-deletes half the table at timestamp 35 from the start, middle, or end. It optionally advances stable and oldest, checkpoints, optionally writes value C at timestamp 45, and validates reads before and after the deletion.

State and persistence behavior: The deleted range can be unstable, stable, or globally visible depending on timestamp advancement. The test validates reads behind the deletion when oldest has not advanced and reads after deletion in all cases.

Dependencies and integration points: Integrates fast-delete, history-store reads through deleted gaps, oldest/stable advancement, checkpoint, eviction, and row/column formats.

Risks: Large deleted gaps can break cursor key ordering or cause missing history when reading behind the delete. Optional new data checks that later updates can repopulate the namespace.

Test signals: Fast-delete stats and exact ordered cursor scans with expected counts and generated values at timestamps 20, 30, 40, and optionally 50.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate13.py -->
