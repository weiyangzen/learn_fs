# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.h

## Purpose

`write_prepared_txn_db.h` declares and partially defines `WritePreparedTxnDB`, the pessimistic transaction DB variant that writes prepared transaction data into the DB before commit and uses commit metadata to decide whether sequence numbers are visible to a snapshot. It is the base visibility and recovery substrate used by write-prepared transactions and by write-unprepared transactions. The file also defines callbacks used by `DBImpl::WriteImpl` to add prepared sequence numbers, add commit entries, publish sequences in two-write-queue mode, and count duplicate-key sub-batches.

## Important APIs, types, and functions

The main type is `WritePreparedTxnDB : public PessimisticTransactionDB`. Public integration points override transaction DB methods: `Initialize`, `BeginTransaction`, `Write`, `Get`, `MultiGet`, `NewIterator`, `NewIterators`, and unsupported coalescing/attribute-group iterator methods. The key public visibility API is `IsInSnapshot(prep_seq, snapshot_seq, min_uncommitted, snap_released)`, which determines whether a value written at a prepare sequence is committed at a snapshot.

`SnapshotBackup` distinguishes real RocksDB snapshots from unbacked sequence-number snapshots. `CommitEntry` stores `<prep_seq, commit_seq>`. `CommitEntry64bFormat` and `CommitEntry64b` compact commit-cache entries into 64 bits by storing the high prepare bits plus commit delta. `PreparedHeap` tracks the smallest outstanding prepared sequence with amortized O(1) erase through a secondary erased heap. `WritePreparedTxnReadCallback` adapts DB reads so `DBIter` can skip uncommitted prepared values. `AddPreparedCallback`, `WritePreparedCommitEntryPreReleaseCallback`, and `WritePreparedRollbackPreReleaseCallback` are `PreReleaseCallback` implementations used during write publication. `SubBatchCounter` splits write batches containing duplicate keys into multiple sub-batches for sequence/visibility accounting.

## Control flow and state behavior

The core read path enters `AssignMinMaxSeqs` to compute `min_uncommitted` and `max` from either a real `SnapshotImpl` or current DB state. A read callback then calls `IsInSnapshot` for candidate sequence numbers. `IsInSnapshot` first handles fast cases: sequence 0 is always visible, sequences greater than the snapshot are not, and sequences below `min_uncommitted` are visible. Otherwise it probes the commit cache, handles races with `max_evicted_seq_`, checks `delayed_prepared_` for long-running prepared transactions, then consults `old_commit_map_` for evicted commit-cache entries that overlap old snapshots. If a snapshot is no longer backed and the metadata needed to distinguish visibility has been dropped, the method returns true but flags `snap_released`.

Prepared writes are added through `AddPrepared`, normally from `AddPreparedCallback` before write sequence numbers are fully visible. Commits call `AddCommitted`, which inserts into the fixed-size commit cache and may advance `max_evicted_seq_`. Advancing the max evicted sequence triggers maintenance over live snapshots, old commit maps, and delayed prepared sets so old reads still know which evicted prepared sequence numbers were committed after their snapshot. `SmallestUnCommittedSeq` reads `prepared_txns_`, `delayed_prepared_`, and `DBImpl::GetLatestSequenceNumber` in a deliberately ordered way to avoid missing in-flight prepared data without taking every lock atomically.

State is mostly in-memory metadata rebuilt or advanced during DB initialization: `snapshot_cache_`, `snapshots_`, `snapshots_all_`, `commit_cache_`, `old_commit_map_`, `delayed_prepared_`, `delayed_prepared_commits_`, and `prepared_txns_`. The durable transaction markers and WAL records live in the underlying DB/WAL; this header defines how in-memory visibility state interprets them after recovery.

## Dependencies and integration points

This file depends deeply on RocksDB internals: `DBImpl`, `DBIter`, `SnapshotImpl`, `PreReleaseCallback`, `ReadCallback`, `SnapshotChecker`, `WriteBatch`, `TransactionDBOptions`, `PessimisticTransactionDB`, and `WritePreparedTxn`. It reaches into `DBImpl` publication behavior, statistics tickers, write queues, WAL prep-section tracking, column-family comparator maps, and `SnapshotImpl::min_uncommitted_`. Write-unprepared code is a friend and reuses protected/private machinery such as `AssignMinMaxSeqs`, `ValidateSnapshot`, `AddPrepared`, `RemovePrepared`, `AddCommitted`, and `ShouldRollbackWithSingleDelete`.

## Risks and edge cases

Correctness depends on memory ordering around `max_evicted_seq_`, `delayed_prepared_empty_`, commit-cache probes, and delayed-prepared cleanup. `IsInSnapshot` contains retry logic and a runtime failure after 100 interrupted max-evicted updates, which signals an unexpected high-contention pattern. The compact `CommitEntry64b` representation assumes commit deltas fit within the configured bit budget; too-large deltas throw. Snapshot release handling is subtle: unbacked snapshots can become invalid once `max_evicted_seq_` passes them. `PreparedHeap` assumes prepare sequence ordering for efficient push/top behavior, and debug assertions guard destructor emptiness except during crash tests. Old snapshots and delayed prepared transactions are expected rare but trigger mutex overhead and logging. Unsupported iterator APIs return `NotSupported`, so callers needing coalescing or attribute-group iterators cannot use this DB mode.

## Test signals

The friend list references extensive write-prepared tests for commit cache, old commit map GC, non-atomic delayed-prepared updates, max-evicted races, snapshot release, recovery, rollback, and smallest-uncommitted behavior. The write-unprepared tests in this work item exercise this header indirectly through read callbacks, recovery, commit/rollback callbacks, WAL prep-section tracking, iterator creation, and snapshot validation.
