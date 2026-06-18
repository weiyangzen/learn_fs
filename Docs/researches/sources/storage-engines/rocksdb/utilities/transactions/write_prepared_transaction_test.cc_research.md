# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_transaction_test.cc

## Purpose

This file is the primary unit and regression test suite for RocksDB's write-prepared transaction mode. It validates the visibility contract where prepared data is already written to the memtable and WAL, but readers must treat it as invisible until a commit marker publishes the prepare sequence through the write-prepared commit map. The tests cover one-write-queue and two-write-queue configurations, ordered and unordered write ordering, optional point-lock-manager modes, crash recovery, compaction behavior, snapshot maintenance, iterator visibility, rollback, direct non-transactional writes through `TransactionDB::Write`, and compatibility with write-committed policy.

The suite also directly tests internal helper structures exposed through friends in `WritePreparedTxnDB`: `PreparedHeap`, `CommitEntry64b`, `AddCommitted`, `RemovePrepared`, `AdvanceMaxEvictedSeq`, `MaybeUpdateOldCommitMap`, `CheckAgainstSnapshots`, `SmallestUnCommittedSeq`, and the snapshot and old-commit data structures. It is therefore both black-box transaction coverage and white-box validation for the data structures that make write-prepared visibility safe under concurrent writes and compaction.

## Important APIs, types, and fixtures

Key type aliases map to `WritePreparedTxnDB::CommitEntry`, `CommitEntry64b`, and `CommitEntry64bFormat`, allowing direct tests of the fixed-size atomic commit cache encoding.

`WritePreparedTxnDBMock` subclasses `WritePreparedTxnDB` and overrides `GetSnapshotListFromDB()` so tests can supply synthetic snapshot lists without using a full DB snapshot list. It also exposes helpers such as `SetDBSnapshots()` and `TakeSnapshot()` to drive `AdvanceMaxEvictedSeq()` and old-commit-map cases.

`WritePreparedTransactionTestBase` extends the shared `TransactionTestBase`. It provides option helpers for `wp_snapshot_cache_bits` and `wp_commit_cache_bits`, `MaybeUpdateOldCommitMapTestWithNext()` for validating snapshot-search pruning, `SnapshotConcurrentAccessTestInternal()` for interleaving `CheckAgainstSnapshots()` and `UpdateSnapshots()`, `VerifyKeys()` for DB and `MultiGet` visibility checks, and `VerifyInternalKeys()` for inspecting exact internal key versions after compaction.

`WritePreparedTransactionTest`, `SnapshotConcurrentAccessTest`, and `SeqAdvanceConcurrentTest` are parameterized fixtures. The main parameter matrix exercises stackable DB disabled, one or two write queues, write-prepared policy, ordered or unordered write ordering, optional per-key point lock managers, and lock timeout variants. Long concurrency tests are split across parameter shards using `split_id_` and `split_cnt_` to keep each instantiation bounded.

## Control flow and coverage map

The early tests validate building blocks. `PreparedHeap.BasicsTest`, `EmptyAtTheEnd`, and `Concurrent` assert that the heap supports monotonic push, O(1)-style deferred erase through an erased heap, resilience to erase-without-push, and concurrent push/erase patterns. `WriteBatchWithIndex.SubBatchCnt` validates duplicate-key sub-batch counting and savepoint rollback behavior, then cross-checks it with `SubBatchCounter`. `CommitEntry64b.BasicTest` exhaustively samples index and delta encodings to ensure compact entries parse back to the original prepare and commit sequences.

Commit map and snapshot tests then cover the core visibility rules. `CommitMap` tests cache add, lookup, CAS exchange, eviction, and index collisions. `MaybeUpdateOldCommitMap`, `OldCommitMapGC`, and `CheckAgainstSnapshots` validate when evicted commit entries must be retained for snapshots satisfying `prepare_seq <= snapshot_seq < commit_seq`. `SnapshotConcurrentAccess` drives all selected interleavings between snapshot-cache readers and writers to ensure live snapshots are not missed while `UpdateSnapshots()` is replacing the cache.

Sequence advancement tests stress the `max_evicted_seq_` frontier. `AdvanceMaxEvictedSeqBasic` verifies that prepared entries at or below the new max move into `delayed_prepared_`, newer prepares remain in `prepared_txns_`, and live snapshots below max are cached. `NewSnapshotLargerThanMax`, `MaxCatchupWithNewSnapshot`, and `MaxCatchupWithUnbackedSnapshot` validate that new snapshots are not allowed to sit at or below `future_max_evicted_seq_`, and that unbacked reads return `TryAgain` instead of using an invalid visibility window. `AdvanceSeqByOne` ensures the dummy transaction trick can bump the last visible/published sequence.

Recovery tests validate persistence. `BasicRecovery` prepares transactions, crashes after WAL flush, reopens, and checks that recovered prepared transactions below max enter `delayed_prepared_`; after committing recovered transactions and reopening again, the delayed set is empty and data is visible. `DisableGCDuringRecovery` ensures recovery does not garbage-collect historical key versions while replaying many entries with a smaller write buffer. `SequenceNumberZero` validates compaction output with sequence number 0 is treated as visible to any snapshot.

Rollback coverage exercises prepared data cancellation. `Rollback` checks rollback before and after crash for Put, Merge, Delete, and SingleDelete cases, including old values and not-found states. `RollbackPreparedAfterCommitWriteFailure` injects retryable write failures into commit and rollback paths, resumes the DB, and verifies rollback can be retried so prepared state is removed before teardown. `BasicRollbackDeletionTypeCb` and `SingleDeleteAfterRollback` validate the optional rollback deletion callback that chooses `SingleDelete` when rolling back a prepared `Put`.

Compaction tests assert that the compaction iterator consults write-prepared visibility rather than just raw sequence ordering. `CompactionShouldKeepUncommittedKeys` and `CompactionShouldKeepSnapshotVisibleKeys` verify uncommitted versions and snapshot-visible older versions survive compaction. The `ReleaseSnapshotDuringCompaction*`, `ReleaseEarliestSnapshotDuringCompaction*`, `ReleaseSnapshotBetweenSDAndPutDuringCompaction`, `ReleaseEarliestWriteConflictSnapshot_SingleDelete`, and `ReleaseEarliestSnapshotAfterSeqZeroing*` tests use sync points to release snapshots while compaction is choosing which keys, deletes, and single-deletes can be dropped or sequence-zeroed. `CompactionKeepSnapshotVisibleKeysRandomized` runs a randomized transaction/snapshot workload and checks all snapshots before and after flush and compaction.

Non-atomic race tests cover the cases where visibility metadata changes in multiple steps. `NonAtomicCommitOfDelayedPrepared` splits reads and commits around delayed prepared cleanup and commit-cache updates. `NonAtomicUpdateOfDelayedPrepared` splits around `delayed_prepared_empty_` and max advancement. `NonAtomicUpdateOfMaxEvictedSeq` splits after reading max but before cache lookup. `AddPreparedBeforeMax` targets the two-write-queue race where a prepare is added while max is being advanced past it. `CommitOfDelayedPrepared` repeatedly takes snapshots between publish and prepared cleanup for delayed prepares with varying commit cache size and sub-batch counts.

The tail of the file covers iterators, policy compatibility, and range tombstone insertion. `Iterate` verifies DB and transaction iterators see the same write-prepared view before and after commit, while `IteratorRefreshNotSupported` documents unsupported refresh. Cross-compatibility tests verify clean write-policy switches and WAL incompatibility failures. The range tombstone tests check that read-path tombstone synthesis is allowed only when it cannot hide prepared entries and includes a regression for sequence-number bumping that could shadow a later committed prepared write.

## State and persistence behavior under test

The test suite repeatedly observes `prepared_txns_`, `delayed_prepared_`, `delayed_prepared_empty_`, `commit_cache_`, `old_commit_map_`, `snapshot_cache_`, `snapshots_all_`, `max_evicted_seq_`, and `future_max_evicted_seq_`. Persistence behavior is centered on WAL markers: prepared batches survive crashes as recovered transactions, commit markers determine whether recovered prepared entries are removed, and sequence number state is checked after WAL flush, reopen, memtable flush, and compaction.

Many tests intentionally shrink `wp_commit_cache_bits` and `wp_snapshot_cache_bits` to force normally rare paths: commit-cache eviction, old-commit-map retention, snapshot cache overflow into the slower vector, and max-evicted advancement. This makes the tests strong signals for bugs that only appear under long-running snapshots, frequent evictions, duplicate-key sub-batches, or two-write-queue commit publishing.

## Dependencies and integration points

The file depends on the transaction test framework (`transaction_test.h`, `transaction_test_util.h`), DB internals (`DBImpl`, internal key inspection, compaction sync points), `FaultInjectionEnv`, merge operators, mock table helpers, `SyncPoint`, perf context counters, and RocksDB public transaction APIs. It integrates with `WritePreparedTxnDB` internals through friend classes and `dynamic_cast`, and with compaction through named sync points in `CompactionIterator`.

## Risks and maintenance notes

The tests rely on internal sequence-number expectations that differ between one-write-queue and two-write-queue modes, so changes to publish semantics or empty commit accounting can require careful updates. Sync-point-heavy tests are sensitive to renamed sync point labels and control-flow restructuring. Several tests intentionally simulate non-recommended use such as erasing non-existent prepared heap entries; those are regression guards and should not be removed just because they look unnatural. Range tombstone tests indicate a newer integration risk: read-path optimization must account for `min_uncommitted` and prepared entries, not only committed tombstone ranges.

## Test signals

This file itself is the test signal for `write_prepared_txn.cc`, `write_prepared_txn.h`, and `write_prepared_txn_db.cc`. High-value signals include crash/reopen cycles, `FaultInjectionTestFS` retryable write failures, small commit/snapshot cache settings, `SyncPoint` race schedules, exact internal-key assertions after compaction, DB and transaction iterator comparisons, `MultiGet` cross-checks, and policy compatibility tests for clean and dirty WAL transitions.
