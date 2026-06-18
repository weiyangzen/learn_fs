# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconGlobalStatsManagerImpl.java

Purpose: Implements `ReconGlobalStatsManager` over the RocksDB `GLOBAL_STATS` column family. It stores simple named counters or stats as `GlobalStatsValue`.

Important APIs: staged manager creation, `reinitialize`, `batchStoreGlobalStats`, `getGlobalStatsValue`, `getGlobalStatsTable`, and `commitBatchOperation`.

State and persistence: opens `ReconDBDefinition.GLOBAL_STATS` as `Table<String, GlobalStatsValue>`. Writers batch string keys and protobuf-backed values, then commit through the shared Recon `DBStore`.

Dependencies and integration: injected from `ReconDBProvider`. This manager is the RocksDB counterpart to the older/generated SQL global stats paths used elsewhere, such as `ReconContainerMetadataManagerImpl` for container count and Om table insight tasks for table-level counts.

Risks: the repository has both SQL global stats and RocksDB global stats abstractions. Callers must be explicit about which store is authoritative for a metric, or Recon can show stale or divergent counters. Like other managers, table initialization errors are logged but not propagated.

Test signals: round-trip tests should cover a null-safe `GlobalStatsValue`, staged manager writes, and batch commit. Integration tests should verify tasks reading global stats use the same storage path as the tasks writing them.
