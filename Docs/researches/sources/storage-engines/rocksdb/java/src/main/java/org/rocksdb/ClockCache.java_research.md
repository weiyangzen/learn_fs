# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ClockCache.java

- **Purpose:** Deprecated compatibility wrapper that preserves the old ClockCache Java API while native implementation returns an LRU-compatible cache due to removal of the old clock cache.
- **Important APIs/types/functions:** Extends `Cache`; constructors accept capacity, optional shard bits, and optional strict capacity limit. Native `newClockCache` creates the underlying replacement cache; disposal uses `disposeInternalJni`.
- **Control flow:** Constructors normalize missing shard bits to `-1` and strict limit to false, then delegate to native allocation.
- **State and persistence behavior:** Native cache is in-memory only. Despite class name, behavior is documented as LRU fallback rather than old clock algorithm.
- **Dependencies:** Depends on `Cache` and native cache factory/disposal functions.
- **Integration points:** Legacy applications using `new ClockCache(...)` and table configs expecting a `Cache`.
- **Risks:** Deprecated class name can mislead performance expectations. HyperClockCache requires extra parameters not represented here. Tests should not assume clock-cache eviction behavior.
- **Test signals:** Constructor compatibility, returned cache usability as block cache, usage metrics, strict-capacity argument propagation, and deprecation/API compatibility checks.
