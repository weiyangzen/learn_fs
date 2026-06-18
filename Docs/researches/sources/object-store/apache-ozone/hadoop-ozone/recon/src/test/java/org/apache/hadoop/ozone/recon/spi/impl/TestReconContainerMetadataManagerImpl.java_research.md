# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconContainerMetadataManagerImpl.java

## Purpose
Tests `ReconContainerMetadataManagerImpl`, the RocksDB-backed manager for container-to-key-prefix mappings, key-prefix-to-container mappings, per-container key counts, and total container count.

## Important APIs, types, and functions
- Uses `ReconTestInjector` with Recon SQL DB, container DB, and Recon OM metadata fixture to obtain `ReconContainerMetadataManager`.
- Exercises `reinitWithNewContainerDataFromOm`, `batchStoreContainerKeyMapping`, `batchStoreContainerKeyCounts`, `commitBatchOperation`, `getCountForContainerKeyPrefix`, `getKeyPrefixesForContainer`, `getContainerForKeyPrefixes`, `getContainers`, `batchDeleteContainerMapping`, `getKeyContainerTable`, `storeContainerCount`, `getCountForContainers`, `incrementContainerCountBy`, and `doesContainerExists`.
- Uses `RDBBatchOperation`, `ContainerKeyPrefix`, `KeyPrefixContainer`, and `ContainerMetadata`.

## Control flow
The static setup creates a shared manager; `@BeforeEach` resets container data. Helper `populateKeysInContainers` writes mappings for two containers. Tests cover reinitialization replacing old mappings with a provided map, batch insertion and counts, per-container key-count overwrites, existence checks, prefix-count lookup, container-to-prefix scans, scans after a previous key prefix, reverse key-prefix-to-container scans, container pagination with previous-container cursor and limit, deletion of one mapping from both directions, and total container count store/increment behavior.

## State and persistence behavior
State lives in the Recon container RocksDB. The manager maintains at least two correlated indexes: container-key-prefix to count and key-prefix-container to count. Batch operations are committed atomically via `RDBBatchOperation`. Reinitialization clears old container metadata and loads new counts, while delete removes both forward and reverse mapping entries.

## Dependencies and integration points
The manager supports Recon APIs that answer "which keys are in a container" and "which containers contain this key prefix." It depends on codec prefix ordering, RocksDB batch semantics, Recon OM metadata manager initialization, and `ReconDBProvider`.

## Risks and edge cases
Bidirectional index consistency is critical; deleting or reinitializing only one side would create stale API results. Cursor semantics for previous container and key prefix are easy to get wrong. Static shared manager setup requires per-test clearing to prevent data leakage.

## Test signals
Signals are exact counts for mappings and containers, zero values for missing prefixes/containers, map sizes and contents for scans, null reverse-table entry after deletion, total container count overwrites/increments, and empty results for invalid cursor/prefix cases.
