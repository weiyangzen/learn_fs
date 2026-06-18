## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStoreImpl.java

Purpose: Implements the witnessed-container metadata store, including singleton-per-DB-path reuse and upgrade compatibility for the old string-valued container IDs table.

Important APIs and functions: Static `get()` computes the DB directory path and returns a cached open store or creates one. `initDBStore()` adds previous-version tables when needed, builds the DB, initializes compatibility tables, and opens the current `ContainerCreateInfoTable`. `getContainerCreateInfoTable()` returns the legacy table until `WITNESSED_CONTAINER_DB_PROTO_VALUE` is finalized. Nested `PreviousVersionTables` wires the old `containerIds` table through a delegated codec.

Control flow and state: A concurrent map caches stores by DB directory. Store initialization is layout-feature dependent. The compatibility codec maps old string state names to `ContainerCreateInfo` with invalid replica index and writes back state names when using the old table.

Persistence and dependencies: Inherits RocksDB lifecycle from `AbstractRDBStore`. Depends on `DBStoreBuilder`, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.WITNESSED_CONTAINER_DB_PROTO_VALUE`, `ContainerID`, `ContainerCreateInfo`, and delegated codecs.

Risks: Cached stores can outlive configuration expectations if DB paths collide. Layout finalization state controls which table is active; changing state across a running process must be coordinated. Legacy records lack replica index, so EC matching treats them as no prior index.

Test signals: Concurrent `get()` reuse, closed store recreation, current table access after finalization, legacy table access before finalization, delegated codec mapping for old states, DB close/isClosed behavior, and `ContainerReader` integration.
