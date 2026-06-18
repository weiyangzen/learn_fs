# sources/storage-engines/rocksdb/util/distributed_mutex.h

Purpose: optional abstraction over folly `DistributedMutex`, falling back to RocksDB's port mutex when folly is unavailable.

Important APIs/types: with `USE_FOLLY`, defines `DMutex` as a subclass of `folly::DistributedMutex` with `kName()` and no-op `AssertHeld()`, plus `DMutexLock = std::lock_guard<folly::DistributedMutex>`. Without folly, aliases `DMutex = port::Mutex` and `DMutexLock = std::lock_guard<DMutex>`.

Control flow: entirely compile-time through `USE_FOLLY`.

State and persistence: mutex state is in-memory synchronization only; no persistence.

Dependencies and integration: includes folly synchronization when available, otherwise `<mutex>` and `port/port.h`. Integration point is code wanting scoped locking while allowing deployments to choose a lower-contention mutex.

Risks: only scoped locking is supported because lock/unlock APIs differ. `AssertHeld()` is a no-op in the folly path, so code must not rely on it for diagnostics. Behavioral/performance differences between fallback and folly can hide concurrency issues.

Test signals: no direct tests in this subset.
