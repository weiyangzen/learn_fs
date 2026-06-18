# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotCache.java

Purpose: `SnapshotCache` is a thread-safe, unbounded custom cache for open `OmSnapshot` DB handles. It reference-counts users, enqueues zero-reference snapshots for eviction, optionally compacts non-snapshot-diff RocksDB tables before close, and exposes write-lock helpers that drain cache entries before destructive operations.

Important APIs and types: the constructor wires a `CacheLoader<UUID, OmSnapshot>`, soft cache size limit, OM metrics, cleanup interval, compaction flag, and OM lock. Public APIs include `get(UUID)`, `invalidate(UUID)`, `invalidateAll()`, `close()`, `release(UUID)`, `lock()`, `lock(UUID)`, and `size()`. It implements `ReferenceCountedCallback`. The `Reason` enum is currently unused.

Get/release flow: `get()` warns through throttled `BatchLogger` if the soft limit is exceeded, acquires a read lock on `SNAPSHOT_DB_LOCK` for the snapshot ID, atomically loads the snapshot through `cacheLoader` if absent, wraps it in `ReferenceCounted`, increments the ref count, updates cache-size metrics, and returns an `UncheckedAutoCloseableSupplier<OmSnapshot>`. The supplier's `close()` decrements the reference count and releases the read lock exactly once. If loading returns `FILE_NOT_FOUND`, `get()` throws an OM file-not-found exception and releases the read lock.

Eviction behavior: when `ReferenceCounted` reaches zero, `callback()` adds the snapshot ID to `pendingEvictionQueue`. Scheduled `cleanup(false)` only acts when cache size exceeds the soft limit; forced cleanup drains pending entries regardless of size. `cleanup(UUID, boolean)` compacts eligible tables when total refs are zero, then atomically removes and closes the snapshot if still unreferenced, decrementing metrics. `invalidate()` closes and removes an entry immediately, independent of ref count, so it should only be used when external locking guarantees no active users.

Locking helpers: `lock()` acquires a resource write lock for all snapshot DBs, forces cleanup, and requires the entire cache to be empty. `lock(UUID)` acquires a write lock for one snapshot ID, forces cleanup of that snapshot, and requires it to be absent. Both return auto-closeable suppliers that release the write lock once.

State and persistence behavior: cache maps and pending queues are in-memory only. Persistent effects are closing RocksDB handles and optional table compaction on snapshot DBs. Metrics track current cache size. The scheduler is optional based on cleanup interval.

Dependencies and integration points: it depends on `CacheLoader`, `ReferenceCounted`, OM lock resources, `OmSnapshot`, `OMMetrics`, `Scheduler`, RocksDB table listing/compaction, and `COLUMN_FAMILIES_TO_TRACK_IN_DAG` to avoid compacting snapshot-diff DAG tables. `OmSnapshotManager` owns the cache, while snapshot reads, diff reads, GC, and checkpoint operations use it to coordinate snapshot DB access.

Risks: the cache is described as LRU but does not track recency; it evicts zero-ref entries from a concurrent set when over limit or forced. `invalidate()` can close a referenced snapshot if misused. `release(UUID)` decrements ref count without releasing the read lock acquired by `get()`, so the auto-closeable supplier path is safer and likely preferred. Compaction before close can add latency to cleanup. `success` of write-lock helpers depends on all readers closing suppliers promptly.

Test signals: `TestSnapshotCache` is extensive and covers metrics, loading, reference counting, eviction, scheduler cleanup, lock draining, error paths, and cache limit warnings. Snapshot diff manager and checkpoint servlet integration tests exercise cache use in larger workflows.
