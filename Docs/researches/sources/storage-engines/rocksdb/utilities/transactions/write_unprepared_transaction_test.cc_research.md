# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_transaction_test.cc

## Purpose

`write_unprepared_transaction_test.cc` is the parameterized unit-test suite for RocksDB's `WRITE_UNPREPARED` transaction policy. It validates read-your-own-write semantics after unprepared flushes, snapshot and iterator visibility, crash recovery, commit and rollback behavior, WAL prep-section retention, savepoints, untracked keys, active iterator invalidation, and range-tombstone synthesis safety.

## Important APIs, types, and functions

The test fixture `WriteUnpreparedTransactionTestBase` derives from `TransactionTestBase` and selects ordered writes plus the supplied write policy. `WriteUnpreparedTransactionTest` parameterizes stackable DB usage, two-write-queue mode, write policy, point-lock manager mode, and deadlock timeout. `WriteUnpreparedSnapshotTest` adds `SnapshotAction` (`NO_SNAPSHOT`, `RO_SNAPSHOT`, `REFRESH_SNAPSHOT`) and `VerificationOperation` (`VERIFY_GET`, `VERIFY_NEXT`, `VERIFY_PREV`).

Tests include `ReadYourOwnWrite` in two forms, `RecoveryTest`, `UnpreparedBatch`, `MarkLogWithPrepSection`, `NoSnapshotWrite`, `IterateAndWrite`, `IterateAfterClear`, `SavePoint`, `UntrackedKeys`, and three range-tombstone tests: `RangeTombstoneMultipleBatchesAndCommit`, `RangeTombstoneCalcMaxVisibleSeqExtendedVisibility`, and `RangeTombstoneOwnDeletionsAndRollback`. The helper `VerifyIterator` normalizes forward and reverse iteration into ascending key vectors.

## Control flow and state behavior

The first read-your-own-write test forces unprepared batches into the DB with `FlushWriteBatchToDB(false)` after repeated writes to keys `a` and `b`; it verifies `Get`, `Seek`, `Next`, `SeekToFirst`, `SeekForPrev`, `Prev`, and `SeekToLast` with and without reseek pressure through `max_sequential_skip_in_iterations`. The snapshot test runs 1000 iterations over five keys, uses a counter as a logical sequence, and verifies that values are before or after the chosen snapshot action for `Get`, forward iteration, and reverse iteration.

`RecoveryTest` varies flush threshold, empty/non-empty previous DB state, action (`UNPREPARED`, `ROLLBACK`, `COMMIT`), and number of batches. It writes named transactions, optionally prepares, simulates WAL flush and crash, reopens without delete, obtains prepared transactions, then commits or rolls back and verifies final contents. `UnpreparedBatch` checks that visible DB iterators hide unprepared data before commit and show only committed data after commit. `MarkLogWithPrepSection` switches WAL files between writes and verifies `TEST_FindMinLogContainingOutstandingPrep` tracks the oldest log containing uncommitted prepared/unprepared data until transactions finish.

Iterator-focused tests cover transactions without snapshots, writing while an iterator is active, and invalidating transaction iterators after commit/rollback. Savepoint and untracked-key tests cover rollback of flushed savepoints and manually appended writes in the underlying `WriteBatch`. The range-tombstone tests set `min_tombstones_for_range_conversion`, use statistics and sync points, and verify that synthesized range tombstones are discarded when the iterator's visible sequence is widened to include a transaction's own unprepared writes.

## Dependencies and integration points

The suite includes `transaction_test.h`, `write_unprepared_txn.h`, and `write_unprepared_txn_db.h`. It relies on RocksDB test helpers such as `ReOpen`, `ReOpenNoDelete`, `TEST_Crash`, `TEST_SwitchWAL`, `FlushWAL`, `GetAllPreparedTransactions`, statistics tickers, `SyncPoint`, and transaction internals exposed through friend declarations. It explicitly casts to `WriteUnpreparedTxn` and `WriteUnpreparedTxnDB` to inspect unprepared sequence maps and DB internals.

## Risks and edge cases

The tests target subtle regressions: reseek loops when write-unprepared iterators need to skip invisible versions, snapshot validation gaps for reverse iteration, crashes between unprepared flush and prepare/commit, WAL deletion while uncommitted data still needs recovery, writes during iteration leaving stale `WriteBatchWithIndex` delta iterators, use-after-clear on transaction iterators, rollback of untracked keys, and range tombstone insertion at widened visible sequence numbers. Parameter combinations cover two-write-queue and lock-manager modes, but they still rely on deterministic single-process test orchestration rather than heavy concurrency.

## Test signals

This file is itself the test signal for the write-unprepared implementation. The strongest behavioral signals are that unprepared data is hidden from normal DB iterators, visible to the owning transaction, durable enough for prepared recovery, rolled back on unprepared recovery, and not allowed to seed unsafe range tombstone optimizations. The tests also assert no range tombstones are inserted when own unprepared deletes participate in the visible deletion run, and they check discarded ticker counts where expected.
