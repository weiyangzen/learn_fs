# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskDbEventHandler.java

Purpose: Shared DB/event mutation logic for namespace summary subtasks.

Important APIs: bucket cache lookup/invalidation, `handlePutKeyEvent`, reprocess variant, `handlePutDirEvent`, reprocess variant, `handleDeleteKeyEvent`, `handleDeleteDirEvent`, `flushAndCommitNSToDB`, `flushAndCommitUpdatedNSToDB`, and `propagateSizeUpwards`.

Control flow and persistence: process-mode handlers merge local map state with existing RocksDB summaries, update file counts, unreplicated and replicated sizes, file-size buckets, child-dir sets, names, and parent IDs, then batch-store/delete through `ReconNamespaceSummaryManager`. Key changes update the immediate parent and propagate deltas to ancestors. Directory changes link or unlink child directory IDs and move existing subtree totals into or out of ancestors.

Dependencies and integration: extended by FSO, Legacy, and OBS namespace tasks. Depends on `ReconOMMetadataManager` bucket lookup, `NSSummary`, `ReconUtils.getFileSizeBinIndex`, and `RDBBatchOperation`.

Risks: recursive propagation depends on correct parent IDs and can silently stop on missing summaries. Delete operations can drive negative counts if events are duplicated or summaries are stale. Reprocess-specific handlers avoid DB reads and therefore rely on later async merge. Bucket cache invalidates only on bucket delete events; missed deletes can use stale object IDs after recreate.

Test signals: test parent propagation for deep trees, delete directory with subtree totals, replicated-size sentinel `-1`, bucket cache invalidation on recreate, hard-delete cleanup, and parity between reprocess and incremental outcomes.
