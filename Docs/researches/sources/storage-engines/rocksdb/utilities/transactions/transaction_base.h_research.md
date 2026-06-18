# sources/storage-engines/rocksdb/utilities/transactions/transaction_base.h

## Purpose

`transaction_base.h` declares `TransactionBaseImpl`, RocksDB's shared internal base class for concrete `Transaction` implementations. It centralizes the public `Transaction` API surface that can be implemented independent of a particular concurrency-control policy: point reads, `GetForUpdate`, multi-get variants, iterators, write operations, savepoints, snapshots, write-batch access, operation counters, lock tracking, and recovery rebuild support. The class remains abstract because subclasses must implement policy-specific locking through `TryLock(...)` and `UnlockGetForUpdate(...)`.

This file is therefore a bridge between the external `rocksdb/utilities/transaction.h` API and the concrete pessimistic/optimistic transaction implementations under `utilities/transactions/`. Its state fields also document the transaction lifecycle: a transaction owns a `WriteBatchWithIndex` for pending writes, optional snapshot state, a `LockTracker`, savepoint metadata, write options, counters, and a commit-time side batch used by two-phase commit modes.

## Important APIs, Types, and Functions

The primary type is `TransactionBaseImpl : public Transaction` declared at line 27. Its constructor accepts a `DB*`, `WriteOptions`, and `LockTrackerFactory`, making both the target database and lock-tracker implementation injectable from the concrete transaction layer. The destructor is virtual via `Transaction`.

The central abstract API is:

- `TryLock(ColumnFamilyHandle*, const Slice&, bool read_only, bool exclusive, bool do_validate, bool assume_tracked)` at lines 39-47. Every tracked write and `GetForUpdate` path is expected to call this before mutating transaction-local state or reading for update.
- `UnlockGetForUpdate(ColumnFamilyHandle*, const Slice&)` at lines 361-363. This is the subclass hook called when `UndoGetForUpdate` determines that a read lock can be released.

Read APIs include `Get`, `GetEntity`, `GetForUpdate`, `GetEntityForUpdate`, `MultiGet`, `MultiGetEntity`, `MultiGetForUpdate`, `GetIterator`, `GetCoalescingIterator`, and `GetAttributeGroupIterator` (lines 55-155). The implementation routes read-your-own-write behavior through `WriteBatchWithIndex` helper methods such as `GetFromBatchAndDB`, `GetEntityFromBatchAndDB`, and multi-get helpers.

Write APIs include `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, plus untracked versions of the same operation families (lines 157-245). The tracked APIs default `do_validate` to `!assume_tracked`, while untracked APIs pass `do_validate=false` and still go through `TryLock` so subclasses can decide how to record or bypass validation.

Snapshot APIs are `GetSnapshot`, `GetTimestampedSnapshot`, `SetSnapshot`, `SetSnapshotOnNextOperation`, and `ClearSnapshot` (lines 255-272). Deferred snapshot creation is represented by `snapshot_needed_` and optional `snapshot_notifier_`.

Savepoint APIs are `SetSavePoint`, `RollbackToSavePoint`, and `PopSavePoint` (lines 49-53). The nested `SavePoint` struct at lines 402-430 captures snapshot state, deferred snapshot state, operation counters, and a `LockTracker` containing locks acquired since that savepoint.

State inspection and support APIs include `GetWriteBatch`, `GetCommitTimeWriteBatch`, `GetTrackedLocks`, `GetNumPuts`, `GetNumPutEntities`, `GetNumDeletes`, `GetNumMerges`, `GetNumKeys`, `GetElapsedTime`, `GetWriteOptions`, `SetWriteOptions`, and `RebuildFromWriteBatch` (lines 247-313).

## Control Flow

For normal tracked writes, callers enter one of the public mutation methods (`Put`, `PutEntity`, `Merge`, `Delete`, or `SingleDelete`). The implementation flow is: call the subclass-defined `TryLock` with `read_only=false` and `exclusive=true`; if it succeeds, append the operation to the write batch returned by `GetBatchForWrite`; then increment the relevant counter. `PutEntity` delegates to `PutEntityImpl`, which follows the same lock-then-batch pattern for wide-column writes.

For untracked writes, the flow is intentionally similar, but validation is disabled. The names do not mean "do not call the lock hook"; they mean the subclass receives `do_validate=false`, which is important for callers that already performed conflict checks or intentionally skip validation.

For `GetForUpdate`, the method first validates option combinations, then calls `TryLock` with `read_only=true` and the requested exclusivity. Only after the key is tracked or locked does it read through `GetImpl`. `MultiGetForUpdate` locks all requested keys first and fails the whole operation if any lock fails, then performs per-key reads. This preserves a simple all-keys-tracked contract for later conflict checking and unlock behavior.

Plain `Get` and `MultiGet` do not acquire update locks. They normalize `ReadOptions::io_activity` where applicable and read through `WriteBatchWithIndex`, ensuring pending transaction-local writes shadow DB state.

Savepoint control flow mirrors two stacks: `write_batch_` owns its own write-batch savepoints, while `TransactionBaseImpl::save_points_` owns transaction metadata. `SetSavePoint` pushes metadata and calls `write_batch_.SetSavePoint()`. `RollbackToSavePoint` restores snapshot/deferred-snapshot state and counters, rolls back the write batch, subtracts locks acquired since the savepoint from the global lock tracker, and pops the metadata savepoint. `PopSavePoint` discards the top savepoint, but when nested savepoints exist it merges the top savepoint's new lock tracker into the next one down so a later rollback still knows which locks were acquired after that older savepoint.

Deferred snapshot control flow is driven by `SetSnapshotOnNextOperation`: it marks `snapshot_needed_` and stores an optional notifier. `SetSnapshotIfNeeded` checks that flag, creates a write-conflict-boundary snapshot through `SetSnapshot`, and notifies the caller after creation. This supports APIs like commit-and-create-snapshot flows without forcing immediate snapshot acquisition.

## State and Persistence Behavior

`TransactionBaseImpl` keeps pending transaction changes in `write_batch_`, a `WriteBatchWithIndex` declared at lines 432-433. This is not durable by itself; it is the in-memory transaction write set that later commit paths consume. When indexing is disabled via `DisableIndexing`, `GetBatchForWrite` returns the underlying `WriteBatch` instead of the indexed wrapper, so future writes are appended but not available through the index for read-your-own-write lookup. That switch is performance-sensitive and changes read visibility of subsequent pending writes.

For two-phase commit configurations, `InitWriteBatch` inserts a noop into the write batch when the batch is empty (lines 368-376). The supporting `.cc` implementation calls it during construction and `Clear` when `DBImpl::allow_2pc()` is true. This ensures prepared transaction batches have the required internal structure even before user writes are appended.

`commit_time_batch_` at lines 451-453 stores extra data to persist with the commit when prepare is not skipped. It is separate from the normal write set so commit-time markers or metadata can be handled by write-committed/write-prepared friends without polluting normal operation counts.

Snapshots are held in `std::shared_ptr<const Snapshot>` with a custom release path declared through `ReleaseSnapshot`. The supporting implementation wraps raw snapshots returned by `DBImpl` so they are released via `DB::ReleaseSnapshot` rather than deleted. `ClearSnapshot` resets the shared pointer and clears deferred snapshot flags.

Lock state lives in `tracked_locks_`, with savepoint-relative lock deltas in `SavePoint::new_locks_`. For pessimistic transactions, tracked locks represent actually acquired locks. For optimistic transactions, the comments clarify they are requested locks used for commit-time conflict checking. The base class deliberately avoids encoding which semantics apply.

`RebuildFromWriteBatch` is a recovery integration hook. The implementation iterates a source `WriteBatch`, strips timestamps from keys when the column family comparator has timestamp size, and replays supported operations through the transaction API. Prepare/commit/rollback markers are rejected for this rebuild path.

## Dependencies and Integration Points

Key dependencies include:

- `rocksdb/utilities/transaction.h` and `transaction_db.h` for the public API contract and transaction DB options.
- `WriteBatchWithIndex` and `WriteBatchInternal` for pending write storage, read-your-own-write lookup, savepoint behavior, 2PC noop insertion, timestamp-size metadata, and protection info.
- `LockTracker` and `LockTrackerFactory` for point-lock tracking, savepoint deltas, and optimistic conflict-check bookkeeping.
- `DB`, `DBImpl`, `ColumnFamilyHandle`, `Snapshot`, `Comparator`, `Iterator`, `PinnableSlice`, and wide-column types for the database-facing API.
- `CoalescingIterator` and `AttributeGroupIteratorImpl` in the implementation for multi-column-family iterator composition.

The class declares `WriteCommittedTxn` and `WritePreparedTxn` as friends, showing that concrete 2PC-capable transaction variants need direct access to private commit-time state. Pessimistic and optimistic transaction classes integrate by deriving from this base and implementing locking/unlocking policy. The point/range lock managers consume the tracked lock requests indirectly through those subclasses.

## Risks and Edge Cases

The highest-risk behavior is the split between validation, tracking, and actual locking. A subclass `TryLock` implementation must interpret `read_only`, `exclusive`, `do_validate`, and `assume_tracked` consistently with the base write/read flows. A mismatch can produce missed conflict detection, leaked locks, or duplicate lock accounting.

Savepoints are another sensitive area. Rollback subtracts locks recorded since the savepoint from the global tracker, while `PopSavePoint` merges nested lock deltas downward. Bugs here can either unlock too much or keep locks longer than intended. Any change to `TrackKey`, `UndoGetForUpdate`, or savepoint merging must be tested with nested savepoints and repeated operations on the same key.

`DisableIndexing` creates a behavioral trap: future writes go directly to the underlying `WriteBatch`, so code expecting reads through `WriteBatchWithIndex` to see all pending writes can be surprised. This should remain a specialized performance option with clear call-site expectations.

Snapshot lifetime is safe only if snapshots always come from the associated `DB` and are released through the custom deleter. Reinitialization changes `db_` and write options, so code paths must avoid carrying old snapshot state across reuse; the implementation calls `ClearSnapshot` during `Reinitialize`.

`MultiGetForUpdate` locks keys sequentially and returns a vector filled with the first lock error if any key fails. Callers should understand partial lock acquisition may have happened before failure and rely on transaction cleanup/rollback for release.

## Test Signals

Relevant tests should cover transaction read-your-own-write semantics, savepoints, rollback/pop with nested savepoints, `UndoGetForUpdate`, untracked operations, optimistic conflict checking, pessimistic lock release, snapshots, 2PC prepared transaction recovery, timestamped keys, wide-column entity operations, and `DisableIndexing`. Good regression signals include transaction DB tests that assert operation counters, `GetNumKeys`, pending batch contents, lock conflict outcomes, and snapshot sequence behavior before and after savepoint rollback.

Integration test names are not declared in this header, but adjacent transaction test suites under RocksDB's `utilities/transactions` area are the right place to look. Changes to this class should also run tests exercising both `WriteCommittedTxn` and `WritePreparedTxn`, since those friend classes rely on private commit-time and write-batch state.
