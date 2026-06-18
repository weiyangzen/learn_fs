<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat15.py

Purpose: verifies `cache_pages_inuse` and `cache_pages_inuse_leaf` connection statistics track cached leaf pages and decrease after cache clearing.

Important APIs/types/functions: `test_stat15` uses `stat.conn.cache_pages_inuse_leaf`, `stat.conn.cache_pages_inuse`, `get_conn_stat`, table cursors, checkpoint, and `reopen_conn`. Connection config enables all stats with a 100MB cache.

Control flow: first test creates a row table, inserts 1000 small records, reads leaf and total page counts, and asserts leaf pages are positive and total pages are at least leaf pages. Second test creates a larger table with 10,000 large records, checkpoints, records leaf pages before reopen, reopens to clear cache, and asserts leaf pages drop.

State and persistence behavior: inserted data populates cache; checkpoint persists the larger table before reopening. Reopen clears in-memory cache state while preserving data on disk.

Dependencies/integration points: covers cache page accounting, connection stats, checkpoint/reopen behavior, and btree page residency. Risks include background pages remaining after reopen or small workloads not allocating pages; signals are positive/increasing relationships and decrease after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat15.py -->
