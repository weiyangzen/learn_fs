# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithLegacy.java

Purpose: Namespace summary subtask for Legacy buckets, supporting both object-store-like and filesystem-path behavior based on OM config.

Important APIs: `processWithLegacy`, `reprocessWithLegacy`, `processWithFileSystemLayout`, `processWithObjectStoreLayout`, `setKeyParentID`, `setParentBucketId`, and `isBucketLayoutValid`.

Control flow and persistence: incremental processing skips bucket-table events except to invalidate bucket cache on delete, processes only `KEY_TABLE`, verifies the bucket layout is LEGACY, then either treats keys ending in `OM_KEY_PREFIX` as directory markers when filesystem paths are enabled or treats all keys as bucket children when disabled. Reprocess scans the Legacy key table, filters by bucket layout, computes parent IDs, applies shared key/dir handlers, and flushes by threshold.

Dependencies and integration: uses `ReconOMMetadataManager` for bucket and parent marker lookups, `OmConfig.ENABLE_FILESYSTEM_PATHS`, `BucketLayout.LEGACY`, and `NSSummaryTaskDbEventHandler`.

Risks: filesystem-path parent reconstruction requires parent marker keys to exist; missing markers throw `IOException` and fail processing. `isBucketLayoutValid` assumes bucket lookup returns non-null. Directory names use full key names, which may matter for endpoint display. Legacy and OBS both interact with key table, so layout filtering is essential.

Test signals: cover legacy filesystem-path mode, object-store mode, missing parent marker, bucket delete/recreate cache invalidation, legacy-vs-OBS filtering, and update events that move size bins or directory markers.
