# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerCache.java

Purpose: This suite verifies `ContainerCache`, the singleton cache that opens and reuses container DB handles as `ReferenceCountedDB` instances. It focuses on eviction behavior, reference counting, concurrent opens, metrics, and recovery when the underlying RocksDB store has been closed.

Important APIs and types: The file uses `ContainerCache.getInstance`, `ContainerCache.clear`, `ContainerCache.getDB`, `ContainerCache.get`, `ContainerCacheMetrics`, `ReferenceCountedDB`, `DatanodeStoreSchemaTwoImpl`, and `VersionedDatanodeFeatures.SchemaV2.chooseSchemaVersion`. `createContainerDB` pre-creates schema-v2 container stores and stops them so the cache can reopen them.

Control flow: `testContainerCacheEviction` creates four DB directories with cache size two, opens repeated references to the same DB, closes selected references, adds more entries, and verifies that referenced entries are not evicted while zero-reference entries are eligible. `testConcurrentDBGet` submits two concurrent `getDB` calls against one path, then closes all references and cleans up. `testUnderlyingDBzIsClosed` manually closes the inner store and expects a later `getDB` to return a new wrapper, while subsequent gets share that new wrapper.

State and persistence behavior: The persistent object under test is an on-disk RocksDB directory. Runtime state is the cache map plus the reference counts. The tests verify cache size, object identity, reference count increments/decrements, cleanup, and the distinction between cached wrapper liveness and underlying store liveness.

Dependencies and integration points: It uses the Ozone container cache configuration key `OZONE_CONTAINER_CACHE_SIZE`, schema-v2 store implementation, Apache commons file cleanup, Java executors, and cache metrics. It does not drive higher-level container operations; it isolates DB handle lifecycle.

Risks: The cache is singleton state, so failure to clear it can contaminate later tests. The concurrent test verifies no exception and final cache size, but does not assert precise reference counts from both worker threads until the final manual cleanup. The eviction test intentionally triggers an `IllegalArgumentException` through over-close behavior, so semantics of `ReferenceCountedDB.close` are part of the signal.

Test signals: Key assertions are cache misses and get-operation counts, stable object identity for repeated live handles, eviction exclusion for referenced entries, null or non-null cache lookups, new handle creation after inner DB close, and cache cleanup leaving no stale state.
