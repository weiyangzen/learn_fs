# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotCache.java

## Purpose
`TestSnapshotCache` validates `SnapshotCache`, the refcounted cache that loads `OmSnapshot` instances, protects snapshot DB access with OM locks, performs deferred eviction/close, compacts snapshot RocksDB tables, and updates OM metrics.

## Important APIs, Types, and Functions
- `SnapshotCache.get(UUID)` returns an `UncheckedAutoCloseableSupplier<OmSnapshot>` handle.
- `release(UUID)`, `invalidate(UUID)`, `invalidateAll()`, `size()`, `totalRefCount(UUID)`, and `getPendingEvictionQueue()` expose cache and eviction behavior.
- `SnapshotCache.lock()` and `lock(UUID)` acquire resource or snapshot-specific write locks and trigger cleanup.
- `IOzoneManagerLock`, `OmReadOnlyLock`, `SNAPSHOT_DB_LOCK`, and `VOLUME_LOCK` verify lock integration.
- Mock `CacheLoader<UUID, OmSnapshot>` creates snapshots with mocked metadata managers and DB stores.

## Control Flow
Setup creates a fresh cache with size limit 3, a mocked cache loader, and metrics. Basic tests load one or more UUIDs and assert cache size and metrics. Lock tests verify read-lock acquisition on `get`, write-lock acquisition on `lock`, and lock release on load/cleanup failures. Eviction tests load/release entries past the soft limit and use `GenericTestUtils.waitFor` to observe asynchronous cleanup. Failure-path tests simulate stale eviction keys, `OmSnapshot.close()` failure retry, and unchecked compaction failure.

## State and Persistence Behavior
The cache state is in-memory but protects persistent snapshot DB handles. `get` increments refcounts and close/release decrements them; entries with zero refcount enter a pending eviction queue. Eviction compacts non-reserved tables before closing snapshots and removes entries from `dbMap` only after successful cleanup. Metrics track current cache size. Snapshot DB compaction intentionally skips DAG-tracked/reserved tables such as `keyTable`.

## Dependencies and Integration Points
The test integrates Guava `CacheLoader`, OM metrics, OM lock hierarchy, `OmSnapshot`, `OMMetadataManager`, and `DBStore`. It also verifies that snapshot operations are not blocked while compaction is waiting by using a semaphore around `compactTable`.

## Risks and Edge Cases
- Timing-dependent eviction tests rely on scheduled cleanup intervals and waits.
- The mocked DB table set is small; production table filtering must remain aligned with the DAG-tracked table list.
- Correctness depends on lock release on every exceptional path because leaked snapshot DB locks can block OM operations.

## Test Signals
Passing signals that cache loading, refcounting, metrics, invalidation, eviction, compaction filtering, and lock cleanup semantics are coherent, including retry behavior after close failure.
