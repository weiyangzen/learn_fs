## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DBStoreManager.java

Purpose: Defines the lifecycle and maintenance contract for datanode RocksDB stores.

Important APIs and functions: `stop()` stops the manager, `close()` is inherited from `UncheckedAutoCloseable`, `getStore()` returns the underlying `DBStore`, `getBatchHandler()` exposes batch transaction support, `flushLog()`, `flushDB()`, and `compactDB()` forward maintenance operations, and `isClosed()` reports thread-safe store closure. `compactionIfNeeded()` is an optional no-op hook.

Control flow and state: This is an interface; implementations decide synchronization and resource ownership. It separates generic DB operations from schema-specific table access.

Persistence and dependencies: It is the common contract used by `DatanodeStore` and `WitnessedContainerMetadataStore`, backed by HDDS `DBStore` and `BatchOperationHandler`.

Risks: Callers may assume `compactionIfNeeded()` has effect for every store, but only schema-specific implementations override it. `getStore()` can return null or closed stores depending on implementation lifecycle.

Test signals: Compile all implementors, verify close/stop/flush/compact paths, ensure batch operations are exposed, and test schema-three compaction override through this interface.
