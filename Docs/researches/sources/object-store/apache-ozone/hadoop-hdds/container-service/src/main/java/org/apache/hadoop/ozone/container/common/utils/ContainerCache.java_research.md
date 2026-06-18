<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java

## Purpose

`ContainerCache` is a singleton LRU cache of schema-v2-style per-container RocksDB `ReferenceCountedDB` handles. It prevents excessive DB open/close churn, provides per-DB-path locking, and closes handles only when their reference count reaches zero. The complete 239-line file was read.

## Important APIs, Types, and Functions

The class extends Apache Commons `LRUMap`. Public methods include `getInstance(ConfigurationSource)`, `getDB(...)`, `removeDB(String)`, `addDB(String, ReferenceCountedDB)`, `shutdownCache()`, and testing `getMetrics()`. It overrides `removeLRU(LinkEntry)`. Internally it uses a global `ReentrantLock`, `Striped<Lock>` keyed by DB path, and `cleanupDb`.

## Control Flow

`getInstance` initializes cache size and lock stripes from Ozone config and registers metrics. `getDB` validates container id, locks the path stripe, checks the map under the global lock, returns and increments an existing open DB, removes closed entries, or opens a new uncached datanode store through `BlockUtils`. After opening, it rechecks the map to avoid duplicate handles, cleans the extra handle if another thread inserted one, then caches and increments the selected handle. LRU eviction calls `cleanupDb` and only removes entries whose handle can be closed.

## State and Persistence Behavior

Runtime state is the LRU map and reference counters. Persistent state is the RocksDB store opened at `containerDBPath`; this class manages handle lifetime but not schema contents. `shutdownCache` attempts to clean every DB and then clears the map.

## Dependencies and Integration Points

It depends on `BlockUtils.getUncachedDatanodeStore`, `ReferenceCountedDB`, Ozone cache config keys, Guava striped locks, Commons `LRUMap`, and `ContainerCacheMetrics`.

## Risks and Edge Cases

Callers must close returned `ReferenceCountedDB` handles exactly once; leaks prevent eviction cleanup, while double close trips the refcount precondition. Extending raw `LRUMap` loses generic type safety. The static metrics/cache lifecycle can conflict with tests or multiple datanode instances in one JVM. `removeDB` increments remove metrics nowhere despite a metrics method existing.

## Test Signals

Tests should cover cache hit/miss/refcount increments, concurrent same-path open deduplication, LRU eviction blocked by positive refcount, cleanup after close, removal of already closed handles, shutdown behavior, metrics increments, and configured cache size/stripe count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerCache.java -->
