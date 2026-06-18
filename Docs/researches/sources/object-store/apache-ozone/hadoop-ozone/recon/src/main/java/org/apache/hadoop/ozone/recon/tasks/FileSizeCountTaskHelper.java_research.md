# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskHelper.java

Purpose: Shared implementation for FSO and OBS file-size count tasks.

Important APIs: `handlePutKeyEvent`, `handleDeleteKeyEvent`, `getFileSizeCountKey`, `truncateFileCountTableIfNeeded`, `reprocess`, `reprocessBucketLayout`, `processEvents`, `writeCountsToDB`, and `buildTaskResult`.

Control flow and persistence: reprocess truncates the RocksDB file-count table once across tasks using `ReconConstants.FILE_SIZE_COUNT_TABLE_TRUNCATED`, then parallel-iterates the relevant OM key table. Each worker accumulates local `FileSizeCountKey -> delta` counts and flushes at a per-worker threshold. Incremental processing walks the OM event batch, converts PUT/DELETE/UPDATE into deltas, and writes them. `writeCountsToDB` reads existing counts, applies deltas, writes positive results, and deletes rows that fall to zero or below.

Dependencies and integration: depends on `OMMetadataManager`, `BucketLayout`, `ParallelTableIteratorOperation`, `ReconFileMetadataManager`, `ReconUtils.getFileSizeUpperBound`, and OM table constants from wrapper tasks.

Risks: read-modify-write is not atomic across concurrent callers; helper comments assume FSO and OBS write disjoint keys, but bucket names may still collide only if volume/bucket identity is unique. `processEvents` logs `value.getClass()` even when value is null, causing possible NPE on null-valued non-delete events. Runtime exceptions from `writeCountsToDB` bubble out of process/reprocess paths.

Test signals: cover concurrent worker flushes, update old/new size bins, delete missing key info, zero-row deletion, truncation reset after failure, and null event values.
