# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.cc

- **Purpose:** Implements `PointLockTracker`, the transaction-side record of point locks acquired or intended by a transaction.
- **Important APIs/types/functions:** Internal iterators `TrackedKeysColumnFamilyIterator` and `TrackedKeysIterator` expose tracked CFs/keys. `Track` records reads/writes, earliest sequence, and exclusiveness. `Untrack` decrements read/write counters and removes empty keys/CFs. `Merge`, `Subtract`, `GetTrackedLocksSinceSavePoint`, `GetPointLockStatus`, `GetNumPointLocks`, iterator factories, and `Clear` implement the `LockTracker` contract.
- **Control flow:** Tracking uses `tracked_keys_[cf][key]`. Repeated tracks increment read or write counts; untrack decrements the matching count. Merge copies or combines counters; subtract removes savepoint-scoped counts. Savepoint delta extraction returns a new tracker containing keys whose current counts are exactly those tracked since the savepoint.
- **State and persistence behavior:** State is an in-memory nested map from column-family id to key to `TrackedKeyInfo` with sequence, read/write counts, and exclusive flag. It is not thread-safe and has no durable persistence.
- **Dependencies:** Depends on `point_lock_tracker.h` and the abstract `LockTracker` API.
- **Integration points:** Created by `PointLockTrackerFactory`, returned by point lock managers, and consumed by transaction code for savepoints and bulk unlock.
- **Risks:** Concrete casts assume same tracker type. `TrackedKeyInfo::Merge` asserts the current sequence is earlier or equal; callers must preserve stronger sequence guarantees. `Subtract` does not erase empty CF maps after removing all keys. `GetKeyIterator` asserts the CF exists.
- **Test signals:** Tests should cover repeated read/write tracking, read/write untracking distinctions, exclusive flag merging, savepoint deltas, iterator traversal, and lock status queries.
