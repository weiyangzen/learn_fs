# sources/storage-engines/tikv/tests/failpoints/cases/test_sst_ingest.rs

## Purpose
This file validates range-latch coordination between SST ingestion paths and the MVCC compaction filter, plus ordering between peer destruction, snapshot application, and foreground writes. It ensures snapshot/clean-overlap ingestion and compaction GC serialize only when their key ranges overlap, while non-overlapping regions proceed independently.

## Important APIs, Types, And Functions
`prepare_data_used_by_compaction_filter` writes multiple MVCC versions with `TikvClient`, splits the keyspace into three regions (`a`, `b`, `c`), and flushes default/write CFs. `setup_cluster` returns a prepared `ServerCluster`, target `Region`, selected `Peer`, and `TestPdClient`. `start_region_migrate` removes and re-adds a peer while forcing SST ingestion via `apply_cf_without_ingest_false` and skipping stale-range cleanup. `start_compaction_filter` runs `TestGcRunner::gc`. Synchronization helpers `verify_pending` and `verify_completed` assert channel progress. Main scenario helpers are `blocked_by_ingest_test` and `blocks_ingest_test`.

## Control Flow
The first matrix starts apply-snapshot or clean-overlap ingestion, pauses after the ingest latch is acquired, then starts compaction-filter GC. For regions `a` and `b`, the GC callback should not fire until the ingestion failpoint is released because their ranges overlap compaction-filter data. For region `c`, the callback should complete immediately because the region does not overlap the relevant GC range. The second matrix reverses the order: compaction GC acquires and pauses on the latch first, then peer migration tries to ingest; overlapping regions block until GC resumes, while region `c` completes without waiting.

`test_apply_snapshot_must_wait_destroy_peer` starts a remove-peer path paused in stale-range cleanup, then re-adds the peer and asserts apply-snapshot completion is blocked until destroy-peer cleanup resumes. `test_destroy_peer_must_wait_ongoing_foreground_writes` pauses a foreground apply write, starts peer destroy, and asserts destroy completion waits for the foreground write failpoint to clear.

## State And Persistence Behavior
The test data has multiple committed versions so compaction filtering has real obsolete MVCC versions to scan. Region boundaries define whether range latches overlap. Persistent writes are flushed to RocksDB default/write CFs. Peer removal/re-addition drives snapshot SST ingestion and stale-range cleanup, while foreground writes and destroy-peer tasks contend through per-region serialization.

## Dependencies And Integration Points
The suite integrates the TiKV transactional KV RPC path, RocksDB CF flushing, region split, PD peer migration, snapshot apply SST ingestion, clean-overlap ingestion, the GC worker's compaction filter, range latch failpoints, and raftstore region-worker ordering.

## Risks And Edge Cases
Risks include deadlocks or missing synchronization between compaction filter and ingestion, over-blocking non-overlapping ranges, boundary overlap mistakes at region start/end keys, concurrent destroy and apply-snapshot with `allow_write` SST ingestion, and destroy-peer racing with in-flight foreground apply writes.

## Test Signals
Blocking is detected by `RecvTimeoutError::Timeout`; successful progress is a channel `Ok(true)`. Thread joins assert no panic. The destroy/apply tests use `apply_snapshot_finished` and `raft_store_after_destroy_peer` callbacks to prove ordering, and failpoint removal should unblock the waiting operation within the expected timeout.
