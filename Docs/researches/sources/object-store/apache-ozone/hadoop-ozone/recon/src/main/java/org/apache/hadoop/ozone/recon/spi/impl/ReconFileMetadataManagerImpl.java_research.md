# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconFileMetadataManagerImpl.java

Purpose: Implements `ReconFileMetadataManager` for RocksDB-backed file-size distribution counts.

Important APIs: staged manager creation, `reinitialize`, `batchStoreFileSizeCount`, `batchDeleteFileSizeCount`, `getFileSizeCount`, `getFileCountTable`, `commitBatchOperation`, and `clearFileCountTable`.

State and persistence: owns the `FILE_COUNT_BY_SIZE` table from `ReconDBDefinition`, keyed by `FileSizeCountKey` and valued by `Long`. It writes only through caller-provided batches and commits those batches through the shared Recon `DBStore`. Clearing the table delegates to `ReconDBProvider.truncateTable`.

Dependencies and integration: injected from `ReconDBProvider`; used by `FileSizeCountTaskHelper`, `FileSizeCountTaskFSO`, and `FileSizeCountTaskOBS`. The table is read-modify-written by helper code during incremental processing and reprocess flushes.

Risks: `initializeTables` logs errors but leaves `fileCountTable` nullable, so later callers can fail with NPEs instead of a clear startup failure. The manager offers no compare-and-swap or locking around read-modify-write counts, so correctness depends on task-level partitioning and flush synchronization. Row-wise truncate can be slow for high-cardinality volume/bucket/size distributions.

Test signals: manager-level tests should store, update, delete, clear, and stage the file-count table. Task tests should assert that zero or negative resulting counts delete rows and that FSO and OBS reprocess truncate only once.
