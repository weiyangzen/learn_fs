# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_tracker.h

- **Purpose:** Defines the transaction-side lock tracking abstraction used to remember lock requests, support savepoints, and drive bulk unlock.
- **Important APIs/types/functions:** Request structs are `PointLockRequest` and `RangeLockRequest`; `PointLockStatus` reports tracked state for a key; `UntrackStatus` distinguishes not tracked, count decremented, and removed. `LockTracker` declares point/range tracking, merge/subtract, clear, savepoint delta extraction, point lock status, lock counts, and column-family/key iterators. `LockTrackerFactory` creates trackers compatible with a manager.
- **Control flow:** Transactions call `Track` after successful lock acquisition, `Untrack` on release/rollback, `Merge` and `Subtract` around savepoints, and iterate tracked column families/keys for unlock.
- **State and persistence behavior:** Trackers are in-memory, not thread-safe, and owned by transactions/savepoints. They persist only logical lock intent/acquisition metadata during transaction lifetime, including sequence numbers and read/write counters in concrete implementations.
- **Dependencies:** Uses RocksDB namespace/status/types and transaction DB endpoint definitions.
- **Integration points:** Concrete managers return a matching factory so pessimistic transactions can maintain tracker state in the right format. Optimistic transactions can use trackers as lock-intention records even without a lock manager.
- **Risks:** Several methods require the argument tracker to be the same concrete type and, for subtract/savepoint operations, to be a subset; violations are enforced by concrete casts/asserts. Iterators are caller-owned and have undefined behavior if used after the underlying tracker mutates.
- **Test signals:** Tests should cover reentrant read/write tracking, untrack counts, merge/subtract, savepoint deltas, iterator coverage, and unsupported point/range no-op behavior.
