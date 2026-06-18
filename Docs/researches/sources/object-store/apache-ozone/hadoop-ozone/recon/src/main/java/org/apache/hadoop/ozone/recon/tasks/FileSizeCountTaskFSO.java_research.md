# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskFSO.java

Purpose: `ReconOmTask` for file-size distribution in File System Optimized buckets.

Important APIs: constructor injection, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess reads parallelism, memory, and flush-threshold configs, then delegates to `FileSizeCountTaskHelper.reprocess` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`. Incremental process delegates to `FileSizeCountTaskHelper.processEvents` for OM `FILE_TABLE`.

Dependencies and integration: writes through `ReconFileMetadataManager`; participates in shared file-count-table truncation through the helper's static flag. Staged task wiring allows snapshot rebuilds into staged Recon DB.

Risks: static truncation coordination spans FSO and OBS; a failed reprocess can leave the truncation flag in a state that must be reset correctly. The task trusts helper read-modify-write operations for counts.

Test signals: verify config propagation, staged manager use, file-table filtering, task name, and reprocess interaction with OBS so the table is truncated once and both layouts repopulate it.
