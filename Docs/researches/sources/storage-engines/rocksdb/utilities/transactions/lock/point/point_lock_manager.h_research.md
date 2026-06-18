# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.h

- **Purpose:** Declares the point-key lock manager implementations used by pessimistic transactions and their deadlock diagnostics.
- **Important APIs/types/functions:** `DeadlockInfoBufferTempl` stores a ring of recent deadlock paths with resize/normalization. `TrackedTrxInfo` captures wait graph neighbors and the key/CF/mode being waited on. `PointLockManager` implements the `LockManager` interface for point locks only. `PerKeyPointLockManager` derives from it and overrides acquisition/unlock to use per-key queues.
- **Control flow:** The declarations define the public manager lifecycle: add/remove column families, try point locks, reject range locks, unlock by key/tracker, report statuses, and resize deadlock buffers. Protected/private hooks split common point-lock logic from per-key behavior.
- **State and persistence behavior:** Declared state includes transaction DB pointer, stripe/lock-count configuration, lock-map mutex/map/cache, key waiter thread-local, wait-for graph maps, deadlock ring buffer, and mutex factory. All state is in-memory and transaction-lifetime scoped.
- **Dependencies:** Depends on transaction APIs, instrumented mutexes, RocksDB hash containers, thread-local utilities, lock manager interface, and point lock tracker factory.
- **Integration points:** Included by `lock_manager.cc`, tests, benchmark tool, and transaction internals. Its `GetLockTrackerFactory` binds point locks to `PointLockTracker`.
- **Risks:** Subclass overrides depend on internal forward-declared `LockMap`, `LockMapStripe`, and `LockInfo` semantics from the `.cc`. The ring buffer `Normalize()` assumes default-constructed empty paths distinguish unused slots.
- **Test signals:** Header-level contracts are tested through manager instantiations, common lock tests, deadlock buffer resize tests, and per-key fairness/efficiency tests.
