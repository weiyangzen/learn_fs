# Research: sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008719`: lines 1-8839, `Docs/researches/chunks/subset-b-008719_research.md`
- `subset-b-008720`: lines 8840-10360, `Docs/researches/chunks/subset-b-008720_research.md`

## Chunk Research

### subset-b-008719: lines 1-8839

# sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc lines 1-8839

Chunk: `subset-b-008719`
Source: `sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc`
Lines covered: 1-8839 of 10360

## Purpose

This chunk contains the first and largest part of RocksDB's transaction test suite for `TransactionDB`, especially the pessimistic transaction implementation. It is not production code; it is a dense regression harness that exercises transaction semantics across write policies (`WRITE_COMMITTED`, `WRITE_PREPARED`, `WRITE_UNPREPARED`), ordered vs. unordered write paths, stackable vs. base DB wrapping, optional two-write-queue behavior, and newer wide-column/secondary-index integrations.

The tests validate that transactions preserve read-your-own-writes behavior, key locking, snapshot validation, two-phase commit lifecycle, WAL recovery, prepared transaction log retention, iterator behavior over DB plus transaction-local deltas, savepoints, lock timeout/deadlock detection, duplicate key handling, commit-time batches, entity/wide-column APIs, coalescing/attribute-group iteration, WAL stall APIs, timestamp comparator restrictions, and secondary-index maintenance. Many cases use crash/reopen cycles and internal `DBImpl` test hooks, making this file a contract for storage-layer state transitions as much as a public API test.

The chunk begins with parameter instantiation and ends in the middle of `SecondaryIndexOnKey`; lines 8840-10360 are owned by `subset-b-008720`.

## Test Fixture And Parameterization

The file includes `transaction_test.h`, DB internals, public RocksDB APIs, secondary-index APIs, sync-point test hooks, transaction utility helpers, merge operators, and the pessimistic transaction DB implementation. The namespace is `ROCKSDB_NAMESPACE`.

Parameterized test suites are instantiated near the top:

- `TransactionTest` runs under `DBAsBaseDB` for non-stackable DB opens with combinations of two write queues, write policies, and write ordering.
- `TransactionStressTest` gets the same broad DB/write-policy coverage for heavier concurrent or long-running cases.
- `StackableDBAsBaseDB` runs a narrower set with the transaction DB stacked over a base DB.
- `MySQLStyleTransactionTest` is enabled outside normal valgrind runs, with an extra boolean parameter for slow-thread variants.

The parameter arrays are wrapped by `WRAP_PARAM_WITH_PER_KEY_POINT_LOCK_MANAGER_PARAMS`, so the same tests also exercise point-lock-manager variations. Several individual tests bypass unsupported combinations at runtime, especially write-unprepared iterator restrictions, write-committed-only wide-column/secondary-index features, blob direct-write path limitations, and two-write-queue-specific stalls.

## Important APIs, Types, And Test Helpers

Core public APIs exercised:

- `TransactionDB::Open`, `BeginTransaction`, `GetTransactionByName`, `GetAllPreparedTransactions`, `GetLockStatusData`, `GetDeadlockInfoBuffer`, `SetDeadlockInfoBufferSize`, `LockWAL`, `UnlockWAL`, `Write` with `TransactionDBWriteOptimizations`.
- `Transaction` methods: `Put`, `PutEntity`, `PutUntracked`, `Merge`, `MergeUntracked`, `Delete`, `DeleteUntracked`, `SingleDelete`, `Get`, `GetEntity`, `MultiGet`, `MultiGetEntity`, `GetForUpdate`, `GetEntityForUpdate`, `MultiGetForUpdate`, `GetIterator`, `GetCoalescingIterator`, `GetAttributeGroupIterator`, `SetSnapshot`, `SetSnapshotOnNextOperation`, `ClearSnapshot`, `SetSavePoint`, `RollbackToSavePoint`, `PopSavePoint`, `UndoGetForUpdate`, `Prepare`, `Commit`, `Rollback`, `SetName`, `GetCommitTimeWriteBatch`, `DisableIndexing`, `EnableIndexing`.
- DB-level operations used as implicit transactions or conflicting actors: `Put`, `PutEntity`, `Delete`, `SingleDelete`, `Merge`, `Write`, `Flush`, `FlushWAL`, `CompactRange`, `CreateColumnFamily`, `CreateColumnFamilyWithImport`, `DropColumnFamily`, `CreateColumnFamilies`, `DropColumnFamilies`, `WaitForCompact`.
- Iterator families: normal `Iterator`, `SecondaryIndexIterator`, `AttributeGroupIterator`, and entity/wide-column accessors such as `PinnableWideColumns` and `WideColumns`.

Internal and test-only integration points:

- `DBImpl` hooks such as `TEST_FlushMemTable`, `TEST_SwitchMemtable`, `TEST_SwitchWAL`, `TEST_FindMinLogContainingOutstandingPrep`, `TEST_FindMinPrepLogReferencedByMemTable`, `TEST_PreparedSectionCompletedSize`, `TEST_LogsWithPrepSize`, `TEST_GetLastVisibleSequence`, `TEST_GetCurrentLogNumber`, `TEST_IsLogGettingFlushed`, `TEST_UnableToReleaseOldestLog`, `PauseBackgroundWork`, `ContinueBackgroundWork`, mutex and write-controller test hooks.
- `PessimisticTransactionDB::TEST_Crash` to simulate process death while retaining files for recovery.
- `SyncPoint` dependencies/callbacks to force interleavings in lock waiting, flush, WAL stall, and write-thread code.
- `RandomTransactionInserter` from the test utilities for MySQL-style invariants.
- `Checkpoint::ExportColumnFamily` and `CreateColumnFamilyWithImport` for imported-column-family transaction writes.

Local helper type:

- `ThreeBytewiseComparator` compares only the first three bytes. It is used to verify duplicate-key detection respects non-default comparators rather than bytewise string identity.

Local nested secondary-index classes:

- `FooSecondaryIndex` in `SecondaryIndexPutEntity` indexes the `foo` wide column, mutates some primary values, emits errors for specific values, derives secondary key prefixes from the last byte, finalizes prefixes, and stores reversed previous-column values as secondary values.
- `KeySecondaryIndex` begins in `SecondaryIndexOnKey` and derives the secondary key prefix from the primary key by removing a three-byte prefix. The test continues in the next chunk.

## Control Flow And Behavioral Areas

### Basic Transaction API And Read-Your-Own-Writes

The early tests confirm the simplest transaction contracts:

- `SuccessTest` and `SuccessTestPinnable` verify `GetForUpdate`, local `Put`, `GetNumPuts`, `GetID`, commit visibility, and both string and `PinnableSlice` read APIs.
- `TxnOnlyTest` verifies transactions work in an otherwise empty DB.
- `DoubleEmptyWrite`, `TwoPhaseEmptyWriteTest`, and `EmptyTest` cover empty `WriteBatch` writes, empty 2PC transactions, empty commits/rollbacks, and read-only transactional commits.
- `WriteOptionsTest` confirms transaction write options are mutable via `SetWriteOptions` and returned by `GetWriteOptions`.
- `CommitWithoutPrepare` distinguishes `skip_prepare=false` returning `IsTxnNotPrepared` from `skip_prepare=true` allowing a direct commit.

### Iterator And Bounds Semantics

Several tests validate `WriteBatchWithIndex`/delta iterator behavior when transaction-local writes are merged with base DB state:

- `TestUpperBoundUponDeletion` and `TestTxnRespectBoundsInReadOption` ensure transaction iterators respect `iterate_lower_bound` and `iterate_upper_bound`, including deletion markers and forward/backward seeks.
- `IteratorTest` checks ordered traversal over committed data plus uncommitted puts/deletes, reverse navigation, seeks around deleted keys, and `GetForUpdate` validation when a key was modified after the transaction snapshot.
- `DisableIndexingTest` shows `DisableIndexing` hides subsequent local writes from transaction reads/iterators until indexing is re-enabled, while earlier indexed writes remain visible.
- `ReseekOptimization` creates many uncommitted entries before a snapshot to verify iterator reseek optimization does not loop indefinitely while skipping hidden prepared/unprepared versions.
- `CoalescingIterator` and `AttributeGroupIterator` cover newer multi-column-family merged iteration. They create two CFs with overlapping and disjoint keys, flush base DB values, add transaction-local values, and verify merged order and per-CF value selection. With `allow_unprepared_value=true`, they require `PrepareValue()` before values/attribute groups are materialized.
- `CoalescingIteratorSanityChecks` and `AttributeGroupIteratorSanityChecks` verify empty CF lists, mismatched comparators, invalid `io_activity`, and unsupported write policies surface `InvalidArgument` or `NotSupported` as appropriate.

### Locking, Conflicts, Deadlocks, And Timeouts

The suite heavily exercises the point lock manager and transaction conflict model:

- `WaitingTxn` validates `GetWaitingTxns`, lock-status introspection, per-CF lock records, perf-context lock wait counters, timeout status text, and post-timeout wait metadata.
- `SharedLocks` covers shared `GetForUpdate` locks, exclusive lock acquisition, upgrade/downgrade expectations, `UndoGetForUpdate`, and lock-status exclusivity flags.
- `DeadlockCycleShared`, `DeadlockCycle`, and `DeadlockStress` build explicit wait-for graphs with sync points and threads. They validate deadlock path contents, buffer ordering, depth-limit behavior, shared-vs-exclusive path metadata, buffer resizing, and high-contention randomized shared/exclusive lock acquisition.
- `WriteConflictTest`, `WriteConflictTest2`, `ReadConflictTest`, `FirstWriteTest`, `FirstWriteTest2`, `PredicateManyPreceders`, and `LostUpdate` establish snapshot validation rules for writes after snapshots, uncommitted locks, reads-for-update, first-sequence edge cases, and lost-update prevention.
- `AssumeExclusiveTracked` clarifies `do_validate` and `assume_tracked`: validation can be bypassed for reads, but the lock is still held; later write operations can assume the key is already exclusively tracked.
- `ValidateSnapshotTest` directly dynamic-casts to `PessimisticTransaction` and calls `ValidateSnapshot` after a prepared transaction commits across flush/history conditions.
- `UntrackedWrites` verifies untracked Put/Merge/Delete variants bypass snapshot conflict tracking but rollback correctly and do not permit later tracked writes to ignore conflicts.
- `ExpiredTransaction`, `TwoPhaseExpirationTest`, `ExpiredTransactionDataRace1`, and `TimeoutTest` cover expiration releasing locks, expired commit failures, db writes waiting for expiration, transaction lock timeout override behavior, and a race where expiration occurs after commit begins.
- `LockLimitTest` and `LockLimitWithTimeoutHangTest` enforce `max_num_locks`, same-key relocking, interaction with timeouts, and a regression where lock-limit plus expired timeout could spin forever.
- `Rollback`, `SavepointTest*`, `UndoGetForUpdateTest*`, and `ReinitializeTest` verify lock release and state reset for rollback, savepoints, popped savepoints, repeated transaction reuse via `BeginTransaction(..., old_txn)`, and manual undo of read locks.

### Two-Phase Commit, WAL, Recovery, And Persistence

The chunk is a major 2PC regression surface:

- `SimpleTwoPhaseTransactionTest`, `PersistentTwoPhaseTransactionTest`, `TwoPhaseRollbackTest`, `TwoPhaseNameTest`, `TwoPhaseDoubleRecoveryTest`, and `TwoPhaseSequenceTest` cover transaction naming, duplicate/invalid names, prepare/commit/rollback sequencing, prepared transaction lookup, durable recovery after crash/reopen, and committed value visibility.
- `CommitTimeBatchFailTest` and commit-time portions of `SimpleTwoPhaseTransactionTest`, `TwoPhaseEmptyWriteTest`, and `SwitchMemtableDuringPrepareAndCommit_WC` validate the special commit-time write batch. Non-empty commit-time batches are invalid unless the transaction is prepared with recovery-specific options. When enabled, commit-time writes survive flush and recovery.
- `LogMarkLeakTest`, `TwoPhaseLogRollingTest`, `TwoPhaseLogRollingTest2`, and `TwoPhaseLogMultiMemtableFlush` assert that WAL log numbers containing outstanding prepares are retained and released at the right time. They differentiate write-committed behavior, where memtables may reference prepare sections, from write-prepared/unprepared policies, where those references should be absent.
- `TwoPhaseOutOfOrderDelete` uses WAL-disabled writes between prepared and logged writes to verify recovery sequence-number accounting does not hide the final WAL-protected value.
- `TwoPhaseLongPrepareTest` keeps a prepared transaction open while many writes, crashes, and reopens happen, then commits the old prepared transaction and validates all data.
- `DoubleCrashInRecovery` corrupts a WAL in point-in-time recovery mode, reopens, optionally writes a later log, crashes/reopens again, and verifies the prepared transaction can still be recovered and committed.
- `DirectWriteCommitPath` validates blob direct-write transaction commit with direct I/O enabled, including post-flush reads.
- `LockWal`, `StallTwoWriteQueues`, and `UnlockWALStallCleared` verify the public WAL lock/stall APIs: prepares and commits should fail while WAL is locked, blocked primary/nonmem write queues should unblock after `UnlockWAL`, and `UnlockWAL` should wait for the stall it owns to be cleared while tolerating unrelated external stalls.

### Column Families, Imported CFs, Timestamp Comparators, And DB Options

Column-family interactions appear throughout:

- `ColumnFamiliesTest` and `ColumnFamiliesTest2` validate transactional writes, deletes, `SliceParts`, MultiGetForUpdate, dropped CF handling, and isolation of same key bytes across CFs.
- `WriteImportedColumnFamilyTest` exports a CF through checkpoint metadata, imports it into a new CF, and verifies transactional writes work against the imported CF.
- `ToggleAutoCompactionTest` opens multiple CFs with different `disable_auto_compactions` settings and confirms mutable CF options preserve the configured values under `TransactionDB::Open`.
- `OpenAndEnableU64Timestamp` allows timestamp-aware comparators only for write-committed transaction DBs; write-prepared/unprepared reject opening/creating such CFs through the transaction layer, even if the underlying `DBImpl` can create one.
- `OpenAndEnableU32Timestamp` rejects non-64-bit timestamp comparator use through transaction DB create/open paths.
- `WriteWithBulkCreatedColumnFamilies` verifies bulk CF creation and drop operations allow transactional DB writes to created handles.

### MultiGet, Merge, Duplicate Keys, And Write Optimizations

The chunk covers batched read/write details:

- `MultiGetBatchedTest`, `MultiGetLargeBatchedTest`, and `MultiGetSnapshot` validate transaction-local batch overlays for deletes, puts, and merges, including >`MultiGetContext::MAX_BATCH_SIZE` paths that force vector-backed autovectors and merge-context allocation. `MultiGetSnapshot` ensures prepared but uncommitted data is hidden from a snapshot taken between prepare and commit.
- `SingleDeleteTest` and `MergeTest` verify transaction read-your-own-writes for single-delete and merge operations and that locks prevent conflicting concurrent merges.
- `MergeOperandFilteringRespectsPublishedBoundary` checks compaction-filter merge operand filtering does not drop operands at/below the published boundary for WC/WP/WU snapshot contexts.
- `DeleteRangeSupportTest` documents that `DeleteRange()` is directly banned, while range deletions via `Write()` are only allowed with the correct `TransactionDBWriteOptimizations` promises. Write-committed needs skipped concurrency control; write-prepared/unprepared also need skipped duplicate-key checking.
- `Optimizations` iterates combinations of `skip_concurrency_control` and `skip_duplicate_key_check` to ensure basic writes remain correct.
- `DuplicateKeys` is a broad duplicate-key contract test. It covers duplicate keys in plain write batches, non-bytewise comparator equivalence, duplicate handling under prepare/rollback/commit-time batches, merge/delete/single-delete combinations, max-successive-merge interaction, savepoint rollback, and crash recovery of prepared duplicate-heavy transactions across default and non-default CFs.
- `MemoryLimitTest` sets a tiny `max_write_batch_size` with no flush threshold and expects the third put to fail with `IsMemoryLimit` without changing the tracked put count.
- `SeqAdvanceTest` uses helper methods from the fixture (`TestTxn0`...`TestTxn4` and `exp_seq`) to assert expected visible sequence-number advancement across transaction patterns, optional flushes, optional WAL flush/reopen branches, and repeated reopen cycles.

### Snapshot Lifecycle

Snapshot-related tests establish precise timing:

- `NoSnapshotTest` permits transactions without a snapshot to read the latest committed value and commit after a later transaction-local write.
- `MultipleSnapshotTest` repeatedly calls `SetSnapshot`, writes at different snapshots, reads through both transaction and DB views, and verifies a later transaction with an older snapshot sees a conflict.
- `DeferSnapshotTest`, `DeferSnapshotTest2`, `DeferSnapshotSavePointTest`, and `SetSnapshotOnNextOperationWithNotification` validate deferred snapshot creation. A plain `Get` does not necessarily instantiate the deferred snapshot, mutating or update-locking operations do, notifiers receive the created snapshot, and savepoint rollback restores deferred/real snapshot state.
- `ClearSnapshotTest` confirms clearing a snapshot returns reads to latest committed state.

### Wide Columns, Entities, Coalesced Attribute Groups

Wide-column/entity APIs are tested under write-committed only:

- `PutEntitySuccess` verifies `PutEntity`, `GetEntity`, `GetEntityForUpdate`, `GetNumPutEntities`, and commit visibility for `WideColumns`.
- `PutEntityWriteConflict` shows transaction-local entity writes are visible to transaction `GetEntity` and `MultiGetEntity`, block conflicting DB-level `PutEntity`, and become visible after commit.
- `PutEntityReadConflict` shows an entity read-for-update at a snapshot locks the key and blocks conflicting DB-level entity writes.
- `EntityReadSanityChecks` verifies invalid arguments for null CF handles, null result buffers, invalid `io_activity`, bad multiget arrays, and `GetEntityForUpdate` with `do_validate=false`.
- `PutEntityRecovery` prepares a transaction with a wide-column entity, reopens, fetches by name, commits, and verifies wide-column persistence.
- `CoalescingIterator` and `AttributeGroupIterator` then exercise entity/value materialization in merged multi-CF iteration, including lazy preparation under `allow_unprepared_value`.

### Secondary Indexes

Secondary-index tests appear at the end of this chunk and continue into the next chunk:

- `SecondaryIndexPutDelete` registers a `SimpleSecondaryIndex` on the default wide column, binds CF1 as primary and CF2 as secondary, writes default-CF and primary-CF records, verifies only eligible primary-CF records produce raw secondary entries, queries through `SecondaryIndexIterator`, updates values through implicit transactions, verifies stale secondary entries are removed/replaced, and finally deletes/single-deletes keys through explicit and implicit transactions to ensure both primary and secondary CFs are empty.
- `SecondaryIndexPutEntity` defines `FooSecondaryIndex` and tests the custom secondary-index callback contract. It verifies errors from `UpdatePrimaryColumnValue`, `GetSecondaryKeyPrefix`, `FinalizeSecondaryKeyPrefix`, and `GetSecondaryValue`; primary-value mutation from `"baz"` to `"quux"`; secondary key/value generation; forward/backward `SecondaryIndexIterator` navigation; and replacement/removal of index entries after DB-level `PutEntity` updates.
- `SecondaryIndexOnKey` starts at line 8772. In this chunk, it defines `KeySecondaryIndex`, which indexes the primary key after stripping a three-byte prefix and rejects too-short keys. The rest of the test's setup/assertions are outside this chunk.

## State And Persistence Behavior

The central persisted state under test is RocksDB key/value data, wide-column entities, WAL contents, prepared transaction metadata, commit-time write batches, and secondary-index entries. Tests deliberately vary when data is in active memtables, immutable memtables, flushed SSTs, WAL-only state, imported CF files, or recovered prepared transaction objects.

Important persistence contracts captured here:

- Prepared transactions are addressable by name after crash/reopen until commit or rollback unregisters them.
- WAL files containing outstanding prepares cannot be released; after commit they may still be retained by memtables in write-committed mode until relevant memtables flush.
- Write-prepared and write-unprepared policies use different visibility/recovery machinery and should not report memtable prepare-log references in places write-committed does.
- Commit-time write batches are only durable/replayable in the supported prepared-transaction mode and may differ across write policies.
- Crash recovery must preserve prepared transactions, duplicate-key semantics, wide-column `PutEntity` data, and valid logs after a point-in-time-corrupted WAL.
- Snapshot and last-visible-sequence behavior must remain stable across flushes, compactions, WAL flushes, and reopen cycles.
- Secondary-index maintenance is transactional: index CF entries are written, updated, and deleted atomically with primary CF changes.

## Dependencies And Integration Points

This file integrates with many subsystems:

- Transaction engine: pessimistic transactions, point locks, deadlock detector, lock manager, transaction name registry, savepoints, tracked/untracked keys, commit-time batches.
- DB core: write queues, write controller stalls, WAL lock/unlock, memtable switching/flushing, compaction, flush scheduling, WAL recovery modes, sequence-number visibility, column-family metadata.
- Storage formats: WriteBatch/WriteBatchWithIndex, merge operators, single-delete semantics, wide columns/entities, blob files/direct write, secondary index encoding.
- Test infrastructure: GoogleTest parameterization, `ROCKSDB_GTEST_BYPASS/SKIP`, `SyncPoint`, fault filesystem, random transaction inserter, mock/plain table factories, checkpoint export/import.
- Performance/context instrumentation: `get_perf_context()` lock wait counters and timing.

## Risks And Maintenance Notes

- Many assertions depend on internal implementation details (`TEST_*` hooks, log-number retention, write-policy-specific memtable references). Correct production changes can require updating these tests rather than preserving exact internals.
- Several tests are intentionally skipped for write-unprepared or non-write-committed policies. Adding support for iterators, entities, coalescing iterators, attribute-group iterators, or secondary indexes in those policies should revisit the bypasses.
- Long-running and threaded tests are gated from regular valgrind because they are expensive and timing-sensitive.
- Sync-point tests can become flaky if internal sync-point names or queue sequencing change without updating dependencies.
- `DuplicateKeys` encodes subtle comparator and duplicate-sub-batch assumptions; changes to WriteBatch duplicate detection, commit-time batch conflict semantics, or recovery replay order can break it.
- WAL and recovery tests mutate real test files and inject corruption; they depend on the fault filesystem and `ReOpenNoDelete` preserving files as expected.
- `SingleDelete` expectations mention undefined DB API behavior after overwrites; these tests document current behavior but are not general semantic guarantees.
- The chunk boundary splits `SecondaryIndexOnKey`, so whole-test conclusions for that case require `subset-b-008720`.

## Test Signals

High-value signals in this chunk:

- Status classes: `OK`, `InvalidArgument`, `NotFound`, `Busy`, `TimedOut`, `Deadlock`, `Expired`, `LockLimit`, `MemoryLimit`, `TxnNotPrepared`, `Incomplete`, `NotSupported`, `Corruption`, `Aborted`.
- Data assertions after commit/recovery verify exact values for regular keys, merged operands, wide-column sets, secondary-index keys/values, and absence after delete/single-delete.
- Lock assertions verify other transactions time out while keys are locked and later succeed after rollback/commit/undo/savepoint rollback.
- Deadlock assertions verify wait-for path shape, exclusivity, CF id, waiting key, timestamps, buffer capacity, and depth-limit metadata.
- WAL/log assertions verify min-log-to-keep, prepared-section heaps, memtable references, unable-to-release-oldest-log flags, and log flush requests.
- Iterator assertions verify seek/next/prev validity, bounded iteration, lazy value preparation, attribute groups, and secondary-index logical keys over raw encoded entries.
- Recovery assertions validate `GetTransactionByName`, `GetAllPreparedTransactions`, commit after crash, and stable data after reopen.

## Cross-Chunk References

This report covers lines 1-8839 only. The following work is visibly incomplete at the boundary and must be reconciled with `subset-b-008720`:

- `SecondaryIndexOnKey` begins at line 8772 and the `KeySecondaryIndex::GetSecondaryValue` method signature is cut off at line 8839. Its full setup, operations, and assertions are in the next chunk.
- The remaining tests listed by the source outline after line 8839 include transaction DB collapse-key behavior, WAL sync with pending prepare, and commit-bypass-memtable tests. They are intentionally not analyzed here except as file-level context for the later merge lane.

### subset-b-008720: lines 8840-10360

# sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc lines 8840-10360

## Chunk Purpose

This chunk covers the tail of `TransactionTest.SecondaryIndexOnKey`, several `TransactionDBTest` cases, and the full `CommitBypassMemtableTest` fixture and test group. The main behavioral focus is transaction correctness around secondary-index iteration, merge operand collapsing, WAL durability for prepared transactions, commit-bypass-memtable writes, snapshot visibility, recovery, merge semantics, deadlock timeout behavior, and automatic large-transaction commit optimization thresholds.

The chunk is test code, but it exercises production integration points across `TransactionDB`, `WriteCommittedTxn`, `DBImpl`, `ColumnFamilyHandle`, merge operators, snapshots, WAL sync/recovery, memtable switching/flush, write queues, and transaction lock management.

## Important APIs, Types, and Functions

- `SecondaryIndex`, `SecondaryIndexIterator`, and `TransactionDBOptions::secondary_indices`: the local `KeySecondaryIndex` maps a primary CF to a secondary CF, indexes the key suffix after a three-byte prefix, and stores a reversed primary key as secondary value.
- `TransactionDBTest` helpers: `ReOpen()`, `ReOpenNoDelete()`, `Put`, `Merge`, `Flush`, `Get`, `GetMergeOperands`, `BeginTransaction`, and `VerifyDBFromMap` are used to assert persisted and in-memory state.
- `Transaction::CollapseKey(ReadOptions, key)`: collapses existing merge operands for one key into a single logical operand while preserving read value semantics.
- `Transaction::SetName`, `Prepare`, `Commit`, and `Rollback`: this chunk exercises prepared transaction lifecycles, named transactions, transaction reuse, and rollback after lock release.
- `TransactionOptions`: key fields under test are `commit_bypass_memtable`, `large_txn_commit_optimize_threshold`, `large_txn_commit_optimize_byte_threshold`, `lock_timeout`, and `deadlock_detect`.
- `CommitBypassMemtableTest`: a parameterized fixture over `(Options::two_write_queues, TransactionDBOptions::use_per_key_point_lock_mgr)` that opens a `WRITE_COMMITTED` `TransactionDB`, enables 2PC, increases `max_write_buffer_number`, and optionally enables `atomic_flush`.
- `DBImpl` test hooks: `TEST_SwitchMemtable()`, `GetLastPublishedSequence()`, `TEST_GetBGError()`, and sync points are used to force precise concurrency and failure windows.
- `SyncPoint`: coordinates writer, flush, WAL creation failure, and bypass decision callbacks. The named sync points around `DBImpl::WriteImpl:AfterWBWIIngestBeforeSetLastSequence`, `DBImpl::InitSnapshotContext:BeforeInit`, `DBImpl::BackgroundCallFlush:ContextCleanedUp`, `DBImpl::SwitchMemtable:AfterCreateWAL`, and `WriteCommittedTxn::CommitInternal:bypass_memtable` are critical test controls.
- Merge support APIs: `MergeOperators::CreateFromStringId("stringappend")`, `MergeOperators::CreateFromStringId("uint64add")`, `GetMergeOperandsOptions`, `PinnableSlice`, and `PutFixed64`.
- Column-family APIs: `CreateColumnFamily`, `CreateColumnFamilies`, `handles_`, `FlushOptions`, per-CF `GetIntProperty(DB::Properties::kNumImmutableMemTable)`, and `ColumnFamilyHandleImpl::cfd()->imm()/mem()` for atomic-flush assertions.

## Control Flow and Tested Behavior

### Secondary Index On Key Tail

The chunk begins inside `KeySecondaryIndex::GetSecondaryValue`, which reverses the primary key and returns it as the secondary value. The test registers the index, reopens the database, creates primary CF `cf1` and secondary CF `cf2`, wires them into the index, inserts keys such as `123foo`, `456bar`, and `789baz` through a transaction, then scans `cf2` through `SecondaryIndexIterator`.

The iterator assertions show the intended ordering and translation: seeking `foo` returns primary keys `123foo`, `456foo`, and `789foo` with values `oof321`, `oof654`, and `oof987`; seeking `bar` and `baz` follows the same suffix grouping. This validates that secondary key prefixes are derived from primary-key suffixes while iterator-visible keys are mapped back to primary keys.

### CollapseKey

`TransactionDBTest.CollapseKey` writes and flushes `hello=world`, then performs two flushed merges on `hello`. Before collapsing, `GetMergeOperands` returns three operands and `Get` resolves to `world,world,world`. A transaction calls `CollapseKey` and commits; afterwards `GetMergeOperands` returns one operand while `Get` still returns the same resolved value. The negative path checks `CollapseKey` on `dummy` returns `NotFound`.

### WAL Sync With Pending Prepare

`FlushedLogWithPendingPrepareIsSynced` reproduces a durability bug where flush skipped syncing an old WAL even though it contained a prepared transaction without its commit record. The test writes a normal key, prepares a named transaction, marks the fault filesystem directly writable so later unsynced records can still be recovered, flushes, commits the prepared transaction, writes another key, reopens without deleting, and verifies all keys. The expected behavior is that the old WAL containing the prepare record is synced before it can be needed by crash recovery.

### CommitBypassMemtable Fixture

`CommitBypassMemtableTest` resets the DB for each configuration, opens `TransactionDB` with `allow_2pc=true`, `write_policy=WRITE_COMMITTED`, `max_write_buffer_number=8`, the test parameter's `two_write_queues`, and the test parameter's per-key point lock manager setting. Tests in this fixture are therefore run across both write queue modes and both lock manager implementations unless explicitly bypassed.

### Single-CF Commit Bypass

`SingleCFUpdate` writes 10,000-key baseline state, takes a snapshot, commits a large transaction using `commit_bypass_memtable=true`, and verifies both snapshot and latest reads before and after flush. It also runs with background work paused, forcing reads from immutable memtables until flush resumes.

`SingleCFUpdateWithOverWrite` builds a layered LSM/memtable state: SST data, a normal transaction moved to immutable memtable, a bypass transaction ingested as WBWI-backed immutable memtables, and a later normal live-memtable update. It tests both `Delete` and `SingleDelete`, snapshots before bypass commit, background-flush-paused and normal modes, immutable-memtable counts, and final flush/compaction. The expected result is that latest state reflects bypass updates/deletes while old snapshots retain pre-bypass state.

### Published Sequence Snapshot Protection

`FlushPreservesPublishedValueDuringBypassOverwriteTwoWriteQueue` and `FlushPreservesPublishedValueDuringBypassOverwriteSingleWriteQueue` force a race in which a bypass commit ingests future versions into immutable memtables before the writer publishes the sequence number. A flush initializes its snapshot context during that gap, and the test takes a snapshot at the old published sequence. The held snapshot must keep seeing `old_value`, while latest reads must see `new_value` after publication.

These tests specifically guard `WRITE_COMMITTED` published-boundary tracking. Without it, flush retention could drop the old visible version because a newer future version exists, leaving the snapshot with `NotFound` or an older delete.

### Multi-CF Commit Bypass

`MultiCFOverwrite` creates three column families, randomizes updates across 10,000 keys, and validates a mix of `Put`, `Delete`, `SingleDelete`, and commit-time write-batch writes. The first transaction always bypasses memtable; the second randomly bypasses. The test tracks expected maps and not-found sets per CF, optionally captures and verifies snapshots between transactions, checks immutable-memtable counts under paused flush, and verifies final state after flush or compaction. CF `meta` exercises `GetCommitTimeWriteBatch()` and should not create bypass immutable memtables.

### Recovery and Sequence Reservation

`Recovery` commits two bypass transactions, reusing the transaction object for the second one, then closes and reopens the DB. The comment explains the key risk: bypass ingest must reserve enough sequence numbers so recovery, which inserts through the normal memtable path, does not produce duplicate key/sequence pairs. Expected values are `k1=v3` and `k2=v4` before and after reopen.

### Large Transaction Optimization Thresholds

`OptimizeLargeTxnCommitThreshold` checks count-based `large_txn_commit_optimize_threshold`. With default options, a 100-op transaction does not bypass. With threshold `10`, a one-op transaction does not bypass and a ten-op transaction does. The same logic is tested across two column families. Explicit `commit_bypass_memtable=true` takes precedence even when the threshold is set high.

`OptimizeLargeTxnCommitWriteBatchSizeThreshold` checks byte-based `large_txn_commit_optimize_byte_threshold`. A large write below default settings does not bypass. With a 100-byte threshold, a transaction whose write batch data size reaches the threshold bypasses, a smaller one does not, and explicit `commit_bypass_memtable=true` still overrides. It also verifies that count-based and byte-based thresholds are OR-like triggers and that byte size is computed across column families.

`WBWIOpCountMismatchWBCount` protects the optimization eligibility check: if code writes directly to the transaction's underlying `WriteBatch` rather than through WBWI-tracked transaction operations, bypass optimization must not apply even if the byte/count threshold would otherwise be met. The direct metadata writes are still committed and readable.

### Atomic Flush

`AtomicFlushTest` opens with `atomic_flush=true`, seeds data into CF1 and CF2, then commits a threshold-sized optimized transaction into CF0. After compaction, all three CFs should have no unflushed immutable memtables and empty mutable memtables. This verifies that bypass optimization cooperates with atomic flush and flushes all relevant non-empty CF memtables consistently.

### SwitchMemtable Failure

`SwitchMemtableFailureStopsDBUntilReopen` injects a retryable WAL creation error at `DBImpl::SwitchMemtable:AfterCreateWAL` during a sync bypass commit. The commit is expected to return `Corruption`, the DB background error becomes fatal corruption, and further writes fail with the same fatal severity. After close/reopen, the prepared transaction's keys are recovered (`k1`, `k2`) and a new write succeeds. This test encodes both failure escalation and recovery expectations.

### Merge Behavior

`MergeAndMultiCF` creates merge-enabled CFs using `stringappend` and `uint64add`, plus a plain data CF. It commits a bypass transaction containing combinations of put, merge, delete, and merge-after-delete, then a normal transaction adding more merge operands. Expected results cover operand resolution (`k1=v1,v2,v3`, `k2=v1`, `k3` not found, numeric count equals 4) and preservation after flush/compaction. With flush paused, it also verifies the raw merge operands for `k1` are visible in order before flushing.

`MergeMiniStress` repeatedly runs 50-operation transactions over random keys with 80% merge, 10% put, and 10% delete probability, randomly choosing bypass or normal commit. It captures a snapshot before each transaction and periodically verifies both current expected state and snapshot state. The loop runs with `min_write_buffer_number_to_merge` set to 1 and 4, exercising different memtable merge-read shapes.

### Lock Timeout Regression

`TransactionDBTest.SelfDeadlockBug` creates two transactions with deadlock detection and a 50 ms lock timeout. Both take shared locks on `shared_key`; then one transaction attempts an exclusive update while the other still holds a shared lock. The expected result is timeout, an empty deadlock-info buffer, and no false self-deadlock report. After rolling back the second transaction, the first can update and roll back.

The chunk then instantiates `TransactionDBTest` for the basic transaction parameter matrix and ends with the file-level `main()` that installs RocksDB's stack trace handler and runs GoogleTest.

## State and Persistence Behavior

- Secondary-index state is persisted through writes to the configured secondary CF and read back via `SecondaryIndexIterator`, which reconstructs primary keys and index values from encoded secondary records.
- Merge state is tested at two levels: logical reads through `Get` and raw operand visibility through `GetMergeOperands`. `CollapseKey` intentionally reduces persisted merge operand count without changing logical value.
- Prepared transaction durability depends on WAL sync ordering. A flushed memtable cannot make an old WAL safely ignorable if that WAL has an unresolved prepare record.
- Commit-bypass-memtable writes produce WBWI-backed immutable memtables instead of first writing to the mutable memtable. Tests verify both read paths before flush and durable recovery after reopen.
- Snapshot state is explicitly preserved across bypass commits, flushes, compactions, and published-sequence gaps. Several tests hold `ReadOptions::snapshot` and compare against copied expected maps.
- Immutable memtable counts are observable state in paused-background-work tests. Expected counts distinguish WBWI immutable memtables, empty immutable memtables created during commit, ordinary immutable memtables, and metadata CFs not involved in bypass ingest.
- Fatal background error state after switch-memtable failure blocks further writes until reopen, but recovery replays the prepared transaction successfully.

## Dependencies and Integration Points

- Depends on RocksDB test infrastructure from `DBTestBase`, transaction test fixtures, `ASSERT_OK`, `SCOPED_TRACE`, `ROCKSDB_GTEST_BYPASS`, and `SyncPoint`.
- Integrates transaction code with lower-level `DBImpl` sequence publication, memtable switching, flush snapshot context, WAL creation/sync, atomic flush, and background error handling.
- Integrates with column-family behavior by mixing primary/data/metadata CFs, merge-enabled CFs, and atomic flush across multiple CF handles.
- Integrates with merge operators by using both string append and fixed-width unsigned addition semantics.
- Integrates with transaction lock managers through fixture parameterization over the per-key point lock manager.
- Uses `fault_fs` to model filesystem durability behavior and direct writability during recovery-oriented tests.

## Risks and Edge Cases Captured

- Secondary index key transformation must preserve grouping, ordering, and value reconstruction for suffix-derived index prefixes.
- `CollapseKey` must not alter logical reads and must return `NotFound` for absent keys.
- WAL sync optimizations are unsafe when old WALs contain prepares that crash recovery may need.
- Flush retention must protect the latest published version, not only explicit snapshots known before a bypass commit publishes its sequence.
- Bypass commit must reserve sequence numbers compatible with normal recovery insertion order.
- `SingleDelete` cases avoid illegal overwrite patterns while still verifying deletion visibility.
- Commit-time write-batch mutations can coexist with bypass transactions but should not cause unrelated CFs to acquire bypass immutable memtables.
- Large-transaction optimization must be disabled when WBWI operation counts diverge from the underlying write batch because direct writes bypass transaction tracking.
- Injected switch-memtable failures must leave the DB in a fatal state rather than allowing partial or ambiguous writes.
- Randomized stress tests can expose ordering bugs, snapshot regressions, and merge operand mishandling that fixed-case tests may miss, but they rely on deterministic test randomness from RocksDB's test random source.

## Test Signals

- Positive signals are mostly `ASSERT_OK`, exact value equality, `VerifyDBFromMap`, immutable-memtable property checks, snapshot sequence checks, and post-reopen verification.
- Negative signals include `IsNotFound` for absent `CollapseKey`, `IsTimedOut` for lock upgrade timeout, `IsCorruption` plus fatal severity for injected switch-memtable failure, and bypass flag callbacks expected to be false in ineligible optimization cases.
- Concurrency-sensitive tests use sync-point dependencies and threads to force writer/flush interleavings that would be difficult to reproduce with timing alone.
- Parameterization multiplies coverage over two write-queue modes and lock-manager choices, with explicit bypasses for tests that target only one write-queue mode.
