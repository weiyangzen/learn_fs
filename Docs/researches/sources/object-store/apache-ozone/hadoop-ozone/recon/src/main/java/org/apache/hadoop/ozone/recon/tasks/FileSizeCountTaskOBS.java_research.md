# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskOBS.java

Purpose: `ReconOmTask` for file-size distribution in Object Store buckets.

Important APIs: constructor, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess delegates to `FileSizeCountTaskHelper.reprocess` with `BucketLayout.OBJECT_STORE`. Incremental process filters OM events to `KEY_TABLE` and delegates to the helper.

Dependencies and integration: shares the `FILE_COUNT_BY_SIZE` table and helper-level truncation flag with `FileSizeCountTaskFSO`. Uses `ReconFileMetadataManager` for RocksDB writes.

Risks: OM key table can include Legacy and OBS concerns elsewhere in Recon; this task relies on layout-specific reprocess and table-level incremental processing. If legacy keys are still present in `KEY_TABLE` events, counts can include unintended buckets unless upstream validation partitions them.

Test signals: cover OBS key table filtering, staged manager behavior, shared truncation with FSO, and update/delete deltas for object-store keys.
