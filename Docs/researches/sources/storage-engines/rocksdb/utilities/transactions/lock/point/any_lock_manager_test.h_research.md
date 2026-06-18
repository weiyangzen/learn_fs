# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/any_lock_manager_test.h

- **Purpose:** Parameterized common tests for lock managers that share point-lock behavior, run against both `PointLockManager` and `PerKeyPointLockManager`.
- **Important APIs/types/functions:** `AnyLockManagerTest` extends `PointLockManagerTest` and `WithParamInterface<init_func_t>`, allowing optional setup functions. Tests use `TryLock`, `UnLock`, `GetDeadlockInfoBuffer`, `GetWaitingTxns`, and `BlockUntilWaitingTxn`.
- **Control flow:** Each test creates a mock column family, begins transactions, acquires locks, and checks reentrancy, upgrade/downgrade, conflict timeouts, shared lock coexistence, deadlock detection, and waiting transaction reporting.
- **State and persistence behavior:** Exercises in-memory lock state and transaction waiting metadata only. No DB data is written beyond opening a test TransactionDB.
- **Dependencies:** Depends on `point_lock_manager_test.h`, RocksDB test harness parameterization, mock column family handles, sync points, and pessimistic transaction objects.
- **Integration points:** Included by `point_lock_manager_test.cc` and instantiated for the base and per-key managers, giving both implementations a shared behavioral baseline.
- **Risks:** Cleanup has a special case because the base `PointLockManager` records repeated shared reentrant locks differently from `PerKeyPointLockManager`. The tests depend on sync point names shared with implementation internals.
- **Test signals:** Reentrant exclusive/shared, lock upgrade/downgrade, conflict timeout matrix, concurrent shared locks, two-transaction deadlock path content, and `GetWaitingTxns` with multiple blockers.
