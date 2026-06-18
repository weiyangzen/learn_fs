<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat08.py

Purpose: checks session-level cache read and transaction dirty-byte statistics, including reset behavior.

Important APIs/types/functions: `test_stat08` uses `wiredtiger.stat.session.bytes_read`, `read_time`, `txn_bytes_dirty`, `stat.conn.cache_bytes_dirty`, `statistics:session`, `statistics:`, and a session opened with `debug=(release_evict_page=true)`.

Control flow: create a table, start a transaction, assert transaction dirty bytes start at zero and do not exceed connection dirty bytes, insert many large values while checking dirty bytes increase, periodically roll back/restart the transaction and verify dirty bytes reset, commit, scan the table, then read session stats for bytes read and page read time. Finally reset the session stats cursor and assert all values are zero.

State and persistence behavior: the test uses a large in-memory workload and explicit transaction boundaries rather than checkpoint/reopen. It validates runtime accounting for dirty bytes and reads into cache after cursor scans.

Dependencies/integration points: covers session stats, connection stats, release-evict debug behavior, transaction accounting, and Windows time-granularity skip. Risks include large loop cost and timing stat portability; signals are monotonic dirty byte changes, positive read stats, and zeroed reset stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat08.py -->
