<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py -->
# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py

Purpose: regression coverage for rollback-to-stable and reconciliation when RTS-created tombstones are later made globally obsolete under a mixed stable/unstable update chain. The test reproduces an out-of-order durable timestamp shape that previously risked invariant failures.

Important APIs/types/functions: `test_rollback_to_stable47` extends `test_rollback_to_stable_base`; it uses `SimpleDataSet`, `wiredtiger.WT_NOTFOUND`, `stat.conn.checkpoint_snapshot_acquired`, `checkpoint_thread`, backup cursors, timestamp helpers, prepared transactions, and `debug=(release_evict)`.

Control flow: create a small row/column table, write stable keys at ts 10 and unstable keys at ts 30, checkpoint, copy a backup, reopen the backup so recovery RTS tombstones unstable keys at stable ts 20, reinsert prepared data at durable ts 26, advance stable/oldest to 30, write newer unstable data at ts 35, then run checkpoint and eviction concurrently under `checkpoint_slow`.

State and persistence behavior: the test deliberately moves data between in-memory update chains, on-disk checkpoint images, backup recovery, and eviction/reconciliation. The persistent signal is that backup recovery removes keys 6-10, while later prepared and unprepared reinserts create the chain shape reconciliation must preserve.

Dependencies/integration points: integrates RTS, backup cursor copying, crash-recovery semantics, checkpoint timing stress, transaction timestamps, prepared updates, eviction, and statistics. Risks are timing sensitivity and hook incompatibilities around timestamp ordering, backup content, and eviction not occurring; assertions verify stable values, missing unstable values, and absence of reconciliation failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable47.py -->
