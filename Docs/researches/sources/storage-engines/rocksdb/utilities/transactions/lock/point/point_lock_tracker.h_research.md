# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.h

- **Purpose:** Declares the concrete point-lock tracker and its singleton factory.
- **Important APIs/types/functions:** `TrackedKeyInfo` stores earliest sequence number, read/write counters, and exclusive flag, with a `Merge` helper. Type aliases define `TrackedKeyInfos` and `TrackedKeys`. `PointLockTracker` implements point tracking, no-op range tracking, merge/subtract/clear/savepoint delta, status, count, and iterators. `PointLockTrackerFactory::Get()` returns a singleton factory.
- **Control flow:** The tracker records point locks by column family and key, while range methods intentionally report unsupported/no-op behavior.
- **State and persistence behavior:** All tracked lock metadata is in-memory transaction state. Sequence numbers represent conflict-check guarantees rather than persisted records.
- **Dependencies:** Depends on C++ memory/string/unordered_map and the abstract `lock_tracker.h`.
- **Integration points:** `PointLockManager::GetLockTrackerFactory` returns this factory, binding point manager acquisitions to this tracker implementation.
- **Risks:** `TrackedKeyInfo::Merge` relies on sequence ordering asserted in debug builds only. Read/write counters are `uint32_t`, so pathological reentrant lock counts could overflow. Unsupported range methods can hide misuse unless callers check capability flags.
- **Test signals:** Header contracts are exercised by transaction savepoint and point-lock manager tests that use tracker-based unlock.
