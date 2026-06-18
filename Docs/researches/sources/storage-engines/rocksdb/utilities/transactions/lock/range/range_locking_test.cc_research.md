# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_locking_test.cc

## Purpose
This non-Windows gtest file exercises RocksDB's range-lock manager through `TransactionDB` and the point-lock-manager compatibility test suite. It validates that range locks conflict with overlapping range and point locks, work under non-default comparators, expose lock-status data, count waits, support waiter access/retry, and trigger lock escalation when enabled.

## Important APIs, Types, And Functions
`RangeLockingTest` owns a temporary `TransactionDB`, `Options`, `TransactionDBOptions`, and a `RangeLockManagerHandle` created by `NewRangeLockManager(nullptr)`. `NewTxn()` wraps `BeginTransaction()` and casts to `PessimisticTransaction`.

The tests cover `Transaction::GetRangeLock()`, `GetForUpdate()`, `Put(..., assume_tracked=true)`, `Commit()`, `Rollback()`, `RangeLockManagerHandle::GetStatus()`, `SetMaxLockMemory()`, `SetEscalationBarrierFunc()`, and `GetRangeLockStatusData()`. `PointLockManagerTestExternalSetup()` adapts `AnyLockManagerTest` to use the range lock manager's point-lock facade.

## Control Flow
The fixture recreates a DB for each test, opens it with `txn_db_options.lock_mgr_handle`, then tests run conflicting transaction sequences. Comparator tests destroy and reopen the DB with reverse-bytewise or timestamp-aware comparators. The lock-wait tests use `SyncPoint` callbacks and a background `port::Thread` to hold a waiter inside range-lock code while another transaction releases locks.

## State And Persistence Behavior
The DB directory is per-thread temporary state and is destroyed in setup and teardown. Locks are in-memory transaction state; tests roll back or commit and delete transactions explicitly. No test asserts durable data beyond using puts to force lock paths.

## Dependencies
The file depends on RocksDB transaction APIs, DB options, `db_impl`, `testutil`, `AnyLockManagerTest`, `TransactionDBMutexFactoryImpl`, `SyncPoint`, and comparator test helpers. The whole file is skipped on Windows because the range-lock tree is not supported there.

## Integration Points
This is the main test signal for the range lock manager integrated with RocksDB's pessimistic transaction layer. It also instantiates the generic point lock manager behavior suite against `NewRangeLockManager(...)->getLockManager()`, making range-lock implementation changes visible to point-lock callers.

## Risks And Edge Cases
The escalation tests are skipped under ThreadSanitizer feature detection and by default on compilers without `__has_feature`, so escalation coverage may be absent in many builds. Lock timeout assertions can be timing-sensitive. Comparator regressions are high risk because range endpoints are raw DBTs without timestamps but must honor user comparator ordering.

## Test Signals
Direct signals include conflicts, reverse comparator length-disparity ordering, timestamp comparator `CompareWithoutTimestamp` behavior, snapshot validation busy status, status reporting for multiple transactions, wait counter increments, waiter wakeup/retry, and generic point-lock behavior.
