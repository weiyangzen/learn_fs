# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTask.java

Purpose: This suite tests the aggregate `NSSummaryTask` that dispatches FSO, Legacy, and OBS namespace-summary work in parallel. It verifies shared executor reuse, reprocess behavior over mixed-layout buckets, process behavior over interleaved layout events, sub-task seek positions, and bucket-cache invalidation on bucket recreation.

Important APIs and types: It uses `NSSummaryTask`, `NSSummaryTask.BucketType`, `ReconOmTask.TaskResult`, `NSSummary`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OmBucketInfo`, `ReconOMMetadataManager`, `ReconConstants`, and reflection against `SUB_TASK_EXECUTOR`. It inherits all OM/Recon fixtures from `AbstractNSSummaryTaskTest`.

Control flow: `setUp` creates one bucket per layout and constructs the aggregate task. Reprocess tests clear stale namespace summaries, run `nSSummaryTask.reprocess`, and assert each bucket's baseline count/size/bin state. Process tests reprocess first, then submit mixed event batches that mutate FSO, Legacy, and OBS buckets. Additional nested tests deliberately interleave layout event order, apply layout-specific seek offsets, run sequential batches, and recreate an OBS bucket under the same name with a new object ID.

State and persistence behavior: The task persists `NSSummary` records keyed by bucket or directory object ID. It updates file counts, byte totals, file-size buckets, child directory sets, and per-layout sub-task seek-position maps. The bucket recreate test also exercises an internal bucket-info cache: bucket-table DELETE/PUT events must invalidate cached object IDs so later key events are attributed to the new bucket ID.

Dependencies and integration points: This is the top-level validation that Recon's namespace summary task composes three layout-specific handlers correctly while sharing the Recon namespace summary manager. It connects OM key-table, file-table, directory-table, and bucket-table events to task controller retry metadata via `TaskResult.getSubTaskSeekPositions`.

Risks: Reflection on a private static executor is brittle. Parallel execution can mask ordering assumptions if handlers share state incorrectly. Seek-position expectations are layout-subtask specific and may need updates if retry semantics change. The recreate test manually updates the bucket table because synthetic events do not apply OM DB writes, so it models but does not fully reproduce production ingestion.

Test signals: Same executor object across task instances, stale `-1` summary removed, exact per-bucket file counts and sizes, file-size bin arrays, successful process result, non-null FSO/Legacy/OBS seek positions, layout filtering that leaves unrelated buckets unchanged, independent seek offsets, and new bucket object ID receiving recreated-bucket key counts.
