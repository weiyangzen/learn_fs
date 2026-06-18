# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconNamespaceSummaryManagerImpl.java

Purpose: Provides wrapper operations for the RocksDB namespace summary table used by Recon namespace APIs and `NSSummaryTask`.

Important APIs: `getStagedNsSummaryManager`, `reinitialize`, `clearNSSummaryTable`, `storeNSSummary`, batched store/delete, `deleteNSSummary`, `getNSSummary`, `commitBatchOperation`, and `getNSSummaryTable`.

State and persistence: opens `NAMESPACE_SUMMARY` from the shared Recon DB, mapping object IDs to `NSSummary` values. The task layer builds and mutates summaries, while this class persists them with direct puts or `RDBBatchOperation` batches. Clear uses row-wise truncation.

Dependencies and integration: injected with `ReconDBProvider` and `NSSummaryTask`. Staged manager creation is used during staged OM snapshot reprocess. The `NSSummaryTaskWithFSO`, Legacy, OBS, and `NSSummaryAsyncFlusher` classes are primary callers.

Risks: a field `nsSummaryTask` is retained only to construct staged managers, which can create circular lifecycle coupling. The raw `Table` return type in `getNSSummaryTable` loses generic safety. Table clear is destructive and depends on `NSSummaryTask` rebuild coordination to avoid concurrent incremental writes into an emptying table.

Test signals: `TestReconNamespaceSummaryManagerImpl` covers basic table operations. Rebuild and endpoint tests should verify clear plus reprocess produces complete bucket, directory, and aggregate rows before queries rely on them.
