# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Cache.java

- **Purpose:** Abstract base for native RocksDB cache wrappers.
- **Important APIs/types/functions:** Extends `RocksObject`; protected constructor accepts a native cache handle. Public APIs are `getUsage()` and `getPinnedUsage()`, both dispatching to JNI.
- **Control flow:** Concrete caches allocate native handles and inherit usage accessors. Accessors assert ownership and call native methods with `nativeHandle_`.
- **State and persistence behavior:** Cache entries and pinned bytes are native in-memory state. There is no durable persistence, but cache lifetime impacts memory pressure and table-reader performance.
- **Dependencies:** Depends on `RocksObject` and native cache usage JNI.
- **Integration points:** Parent for `LRUCache`, `ClockCache`, HyperClock cache wrappers, and table/backup option references to caches.
- **Risks:** Assertions are optional; use after close can reach JNI with an invalid handle. Options retaining cache handles require the cache object to outlive users.
- **Test signals:** Usage/pinned usage values before and after database/table reads, disposal behavior, and integration with block-based table configs.
