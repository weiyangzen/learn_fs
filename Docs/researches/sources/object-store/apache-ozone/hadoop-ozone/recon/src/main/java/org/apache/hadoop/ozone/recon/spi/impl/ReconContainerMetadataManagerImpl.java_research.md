# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconContainerMetadataManagerImpl.java

Purpose: Implements `ReconContainerMetadataManager`, the Recon-side service for container/key reverse indexes, per-container key counts, replica history, and the total container count. It binds Recon's internal RocksDB column families from `ReconDBDefinition` and also uses the generated SQL `GlobalStatsDao` for `CONTAINER_COUNT_KEY`.

Important APIs: staged manager creation over a staged `DBStore`, `reinitialize`, `reinitWithNewContainerDataFromOm`, batched store/delete for `ContainerKeyPrefix` and `KeyPrefixContainer`, `getKeyPrefixesForContainer`, `getContainerForKeyPrefixes`, `getContainersIterator`, replica history getters/setters, and `incrementContainerCountBy`. It exposes table accessors for tests and iterator-based callers.

Control flow and persistence: initialization opens `CONTAINER_KEY`, `KEY_CONTAINER`, `CONTAINER_KEY_COUNT`, and `REPLICA_HISTORY_V2`. If `KEY_CONTAINER` is empty, it backfills it from `CONTAINER_KEY`. Writes maintain both forward and reverse key mappings when a key prefix is present, and commit through `RDBBatchOperation`. `reinitWithNewContainerDataFromOm` truncates container tables, repopulates mappings, and resets SQL container count to zero.

Dependencies and integration: depends on `ReconDBProvider`, `ReconOMMetadataManager`, codecs for `ContainerKeyPrefix` and `KeyPrefixContainer`, JOOQ SQL configuration, and OM key tables for pipeline lookup. Container-key mapper tasks are its primary writers; API endpoints likely page through `getKeyPrefixesForContainer` and `getContainers`.

Risks: `getPipelines` builds a stream but does not terminally consume it, so pipelines may never be added. `getContainersIterator.next` increments `numberOfKeys` by one per prefix row instead of using stored counts. `initializeTables` logs but does not fail fast on table-open errors. Container count writes are read-modify-write through SQL and can race across tasks.

Test signals: existing tests include `TestReconContainerMetadataManagerImpl`; useful coverage should include reverse-index backfill, pagination from a non-existent or exact previous key, staged-manager behavior, replica history V2 persistence, and concurrent container count updates.
