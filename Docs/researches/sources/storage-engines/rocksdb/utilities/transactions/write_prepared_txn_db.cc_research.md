# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.cc

## Purpose

This file implements `WritePreparedTxnDB`, the DB-level transaction engine for write-prepared mode. It owns the visibility metadata that lets RocksDB store uncommitted prepared data in memtables and SSTs while presenting snapshot-correct committed views to readers and compaction. The implementation manages recovery initialization, direct writes, reads and iterators with visibility callbacks, prepared sequence tracking, commit-cache insertion and eviction, snapshot-cache maintenance, old-commit retention for long-running snapshots, and duplicate-key sub-batch counting.

## Important APIs and functions

`Initialize()` rebuilds prepared state from `DBImpl::recovered_transactions()`, adds each recovered prepare sequence in order, advances `max_evicted_seq_` to the latest sequence, creates a sequence gap after recovery, installs `WritePreparedSnapshotChecker`, installs a recoverable-state pre-release callback for flush-time recovered state, and delegates remaining setup to `PessimisticTransactionDB::Initialize()`.

`VerifyCFOptions()` extends the pessimistic DB checks by requiring a memtable factory that can handle duplicated keys. This is required because prepared/uncommitted and committed versions of the same user key can coexist.

`BeginTransaction()` creates or reinitializes `WritePreparedTxn`. `Write()` overloads route direct writes either through pessimistic locking or through `WriteInternal()` when concurrency control is explicitly skipped.

`WriteInternal()` handles non-2PC writes under write-prepared visibility. It updates per-key protection info if needed, computes `batch_cnt` with `SubBatchCounter` when not provided, inserts a noop separator, writes the batch with memtable enabled, and in two-write-queue mode performs a second empty memtable-disabled write that publishes the commit sequence. Pre-release callbacks either add prepared state before the publish step or directly update the commit map in one-write-queue mode.

`Get()`, `GetImpl()`, and `MultiGet()` run reads through `WritePreparedTxnReadCallback`. `GetImpl()` returns `TryAgain` if an unbacked snapshot became invalid because `max_evicted_seq_` advanced during the read. Timestamp-returning overloads are explicitly unsupported.

`NewIterator()` and `NewIterators()` create DB iterators with write-prepared callbacks. If the caller did not provide a snapshot, the DB takes an owned snapshot and stores it in `IteratorState` so commit-map entries needed by the iterator cannot be garbage-collected before iterator cleanup. Iterator refresh is disabled by passing `allow_refresh = false`.

`Init()` sizes and zero-initializes the snapshot cache and commit cache from transaction DB options, sets the dummy max snapshot, and stores the rollback deletion callback.

`AddPrepared()`, `CheckPreparedAgainstMax()`, `RemovePrepared()`, and `SmallestUnCommittedSeq()` manage prepared state. Recent prepared entries live in `prepared_txns_`, a monotonic heap optimized for cheap top reads and deferred erase. When `max_evicted_seq_` advances past prepared entries, `CheckPreparedAgainstMax()` moves them to `delayed_prepared_` so `IsInSnapshot()` can still detect them without searching the heap for old sequences. `RemovePrepared()` clears both structures and any delayed commit metadata for all sub-batches.

`AddCommitted()` inserts a `prepare_seq -> commit_seq` entry into the fixed-size atomic commit cache. When the target cache slot already contains another valid entry, the evicted entry can advance `max_evicted_seq_`; if it overlaps a live snapshot, `CheckAgainstSnapshots()` preserves enough information in `old_commit_map_` so old snapshots still know the evicted prepare was not yet committed. The update uses `ExchangeCommitEntry()` with retry protection.

`AdvanceMaxEvictedSeq()` publishes a future max first, moves prepared entries below the new max into delayed state, fetches live snapshots below max from the DB, updates snapshot caches, initializes old-commit-map buckets for those snapshots, and finally advances `max_evicted_seq_`. `GetSnapshotInternal()` uses `future_max_evicted_seq_` to avoid returning a new snapshot at or below a max whose snapshot list has not yet been captured; in rare cases it calls `AdvanceSeqByOne()` until a larger snapshot is available.

`UpdateSnapshots()`, `CleanupReleasedSnapshots()`, `ReleaseSnapshotInternal()`, `CheckAgainstSnapshots()`, and `MaybeUpdateOldCommitMap()` implement snapshot metadata maintenance. A small atomic `snapshot_cache_` serves lock-free-ish readers; overflow snapshots live in `snapshots_` under `snapshots_mutex_`. Released snapshots trigger old-commit-map cleanup once they are at or below max. Evicted commit entries are retained only for snapshots in the overlap window `prep_seq <= snapshot_seq < commit_seq`.

`SubBatchCounter` counts sub-batches in a write batch by tracking duplicate keys per column family. A duplicate key starts a new sub-batch so each sub-batch has no duplicate user key under its comparator.

## Control flow

Direct write flow begins in `Write()`. If locking is skipped, `WriteInternal()` inserts the batch into DB and creates commit visibility metadata. With two write queues, the first write inserts data and adds prepared state; a second empty WAL-disabled, memtable-disabled write publishes commit metadata from the nonmem queue. With one write queue, one callback can add commit entries because sequence publication is coupled with the write.

Read flow begins by assigning a max sequence and min uncommitted sequence. If a real snapshot exists, its enhanced `min_uncommitted_` and sequence number are used. If no snapshot exists, `SmallestUnCommittedSeq()` supplies the lower bound and DB internals later choose a visible max. `WritePreparedTxnReadCallback::IsVisibleFullCheck()` calls `IsInSnapshot()` for candidate internal sequence numbers. If the callback discovers an unbacked snapshot was effectively released, the read reports `TryAgain`.

Commit-cache eviction flow is the central maintenance loop. `AddCommitted()` may evict an older entry from `commit_cache_`; that entry's commit sequence can become the new `max_evicted_seq_` or contribute to a stepped max advance. Advancing max requires moving old prepares, collecting snapshots, updating snapshot caches, potentially populating `old_commit_map_`, and only then publishing `max_evicted_seq_`.

Snapshot flow is two-sided. Taking a snapshot computes `min_uncommitted_` before getting the DB snapshot and rejects snapshots at or below future max. Releasing a snapshot calls `ReleaseSnapshotInternal()` so old-commit-map rows can be removed when no longer needed.

## State and persistence behavior

Most state is in memory and rebuilt or conservatively reset on recovery. `prepared_txns_` and `delayed_prepared_` represent uncommitted prepared data. `commit_cache_` is an in-memory acceleration structure for recent commits. `max_evicted_seq_` marks the range where cache absence is ambiguous and may require old snapshot metadata. `old_commit_map_` stores only evicted prepare sequences that are not visible to specific old snapshots. `snapshot_cache_`, `snapshots_`, and `snapshots_all_` track live snapshots below max. `future_max_evicted_seq_` prevents new snapshots from escaping the capture window during max advancement.

Persistent behavior comes from WAL and sequence numbers rather than from these in-memory maps. Recovery reads prepared transactions from `DBImpl`, reconstructs prepared state, advances max to the latest sequence, and sets `LastAllocatedSequence`, `LastSequence`, and `LastPublishedSequence` to `last_seq + 1` to create a clean gap after recovery. Commit and rollback markers in WAL determine whether recovered prepares remain uncommitted or become visible.

## Dependencies and integration points

This implementation integrates deeply with `DBImpl`, `versions_`, `WriteImpl`, `NewIteratorImpl`, `SetSnapshotChecker`, `SetRecoverableStatePreReleaseCallback`, `logs_with_prep_tracker`, `ManagedSnapshot`, column family handles and comparators, `PreReleaseCallback`, `ReadCallback`, `TransactionUtil`, and `PessimisticTransactionDB`. It uses `SyncPoint` labels as test hooks and statistics tickers such as `TXN_GET_TRY_AGAIN`, `TXN_DUPLICATE_KEY_OVERHEAD`, `TXN_PREPARE_MUTEX_OVERHEAD`, `TXN_SNAPSHOT_MUTEX_OVERHEAD`, and `TXN_OLD_COMMIT_MAP_MUTEX_OVERHEAD`.

## Risks

The main correctness risk is non-atomic coordination among commit cache, delayed prepared state, snapshot caches, old commit map, and max advancement. The code relies on ordering rules: `future_max_evicted_seq_` is updated before fetching snapshots; prepared entries are copied to delayed state before removal from the heap; commit entries are installed before publishing; prepared entries are removed after publishing. Violating any of these can expose uncommitted values, hide committed values, or allow compaction to drop required versions.

Another risk is cache sizing and entry encoding. `CommitEntry64b` can encode only commit deltas below the format's upper bound; workloads with very large gaps between prepare and commit can hit the runtime guard. Duplicate-key sub-batch accounting must remain consistent with sequence allocation or `RemovePrepared()` and `AddCommitted()` will cover the wrong sequence range. Iterator ownership is also sensitive: without an owned snapshot, a no-snapshot iterator could outlive the commit-map metadata it needs.

## Test signals

`write_prepared_transaction_test.cc` directly covers most paths in this file. High-signal tests include `CommitMap`, `CommitEntry64b.BasicTest`, `OldCommitMapGC`, `CheckAgainstSnapshots`, `SnapshotConcurrentAccess`, `AdvanceMaxEvictedSeqBasic`, `MaxCatchupWithNewSnapshot`, `MaxCatchupWithUnbackedSnapshot`, `CleanupSnapshotEqualToMax`, `SmallestUnCommittedSeq`, `BasicRecovery`, `Rollback`, the non-atomic delayed-prepared/max tests, `AddPreparedBeforeMax`, `CommitOfDelayedPrepared`, iterator tests, and compaction/snapshot-release tests.
