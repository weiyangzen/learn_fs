# sources/storage-engines/wiredtiger/test/suite/test_debug_mode09.py

Purpose: tests `debug_mode=(update_restore_evict=true)`, which forces update-restore eviction under cache pressure.

Important APIs and control flow: connection config sets a small cache, all statistics, low `eviction_target`, and update-restore debug mode. `trigger_eviction` writes 20000 rows in separate transactions, each with a 500-byte value. The test then reads `stat.conn.cache_write_restore_scrub` from the connection statistics cursor.

State and persistence: repeated committed updates pressure cache and eviction. The statistic is persistent only as runtime stats, not table data.

Dependencies and integration: uses `wiredtiger.stat`, `wttest`, transaction APIs, and `statistics:`.

Risks and test signals: eviction behavior depends on cache pressure. The test mitigates that with a low target and large data volume. Success requires the restore-scrub counter to become greater than zero.
