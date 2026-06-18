# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithOBS.java

Purpose: Namespace summary subtask for Object Store buckets.

Important APIs: `reprocessWithOBS`, `processWithOBS`, private `processKeyTableInParallel`, and `getKeyParentID`.

Control flow and persistence: reprocess scans the object-store key table in parallel, checks each key's bucket layout from the bucket table, resolves parent object ID to the bucket object ID, accumulates worker-local summary deltas, and submits them to `NSSummaryAsyncFlusher`. Incremental processing invalidates bucket cache on bucket delete, filters to `KEY_TABLE`, validates value type, filters to OBJECT_STORE buckets, and applies key PUT/DELETE/UPDATE as bucket-child changes.

Dependencies and integration: extends the shared DB event handler, uses `ReconOMMetadataManager`, OM bucket table, `BucketLayout.OBJECT_STORE`, `ParallelTableIteratorOperation`, and `ReconNamespaceSummaryManager`.

Risks: reprocess performs bucket table lookups per key without the shared cache, which can be expensive. Process path assumes bucket lookup is non-null before calling `getBucketLayout`. OBS update assumes keys cannot move between buckets in an UPDATE event. Parent lookup failure aborts the subtask.

Test signals: cover bucket layout filtering, null bucket info, bucket delete/recreate cache invalidation, update with old value, reprocess parallel flush, and parent ID assignment to bucket object ID.
