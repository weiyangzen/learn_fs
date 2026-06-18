# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.h

- **Purpose:** Defines the abstract locking interface used by pessimistic transactions, covering point locks, range locks, lock tracking, status inspection, deadlock diagnostics, and deadlock buffer resizing.
- **Important APIs/types/functions:** `LockManager` declares `IsPointLockSupported`, `IsRangeLockSupported`, `GetLockTrackerFactory`, `AddColumnFamily`, `RemoveColumnFamily`, point/range `TryLock`, point/range/tracker `UnLock`, `GetPointLockStatus`, `GetRangeLockStatus`, `GetDeadlockInfoBuffer`, and `Resize`. It aliases point and range status multimaps.
- **Control flow:** Transactions acquire locks through `TryLock`, record them using a compatible `LockTracker`, and later release individual locks or all tracked locks. Managers are dynamically configured as column families are added or removed.
- **State and persistence behavior:** Implementations keep in-memory lock state only; the interface has no durable persistence. Status APIs expose current in-memory lock holders and wait/deadlock diagnostics.
- **Dependencies:** Depends on RocksDB transaction/TransactionDB types, column family identifiers, `Endpoint`, `KeyLockInfo`, `RangeLockInfo`, `DeadlockPath`, and `LockTracker`.
- **Integration points:** Used by `PessimisticTransactionDB` and transaction objects; concrete point and range managers implement the interface.
- **Risks:** Correctness depends on matching the manager with the tracker factory returned by `GetLockTrackerFactory`. The caller must honor column-family lifecycle preconditions documented in comments.
- **Test signals:** Any lock-manager implementation should pass common tests for capability flags, point/range unsupported behavior, lock conflict semantics, status reporting, deadlock buffer behavior, and tracker-based unlock.
