<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config11.py

Purpose: tests session debug reconfiguration `debug=(release_evict_page=true)`, which evicts pages as they are released.

Important APIs and control flow: scenarios cover record-number and integer-row keys. The test creates an unlogged table, measures max cache size, inserts enough 4KB-ish values through a snapshot-isolation session to reach roughly 75% cache use, checkpoints to clean pages, reads all content without debug eviction and verifies cache stays high, then reconfigures the session and rereads to assert cache usage drops by more than half.

State, persistence, and dependencies: state includes many clean pages in cache and connection cache statistics. Dependencies are `SimpleDataSet`, `wiredtiger.stat`, `session.reconfigure`, snapshot transactions, and cache/eviction behavior.

Integration points: covers runtime session reconfiguration and debug eviction code paths that operate after page release.

Risks and test signals: cache-size thresholds are workload and eviction sensitive. The pass signal is relative cache usage before/after debug reconfiguration while all values remain readable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config11.py -->
