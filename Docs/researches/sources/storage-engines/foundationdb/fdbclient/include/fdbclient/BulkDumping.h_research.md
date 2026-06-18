# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BulkDumping.h

Purpose: defines bulk dump job/task metadata and creation API, using bulk-load manifests as the export format.

Important APIs and types: `BulkDumpPhase` has invalid/submitted/complete. `BulkDumpState` stores job id, job range, phase, optional task id, and `BulkLoadManifest`. It exposes getters for job/task/range/root/transport/type/manifest, validity checks, `generateRangeTask`, `generateBulkDumpMetadataToPersist`, serialization, equality, and diagnostics. `createBulkDumpJob` is the user-facing metadata constructor.

Control flow: a user job starts with a valid job ID/range/root and submitted phase. `generateRangeTask` clones job config, generates a distinct task ID, and narrows the manifest range. Completed storage-server output calls `generateBulkDumpMetadataToPersist` with a full manifest and sets phase complete.

State and persistence: `BulkDumpState` is serialized metadata for job and completed task state. Task instances sent to storage servers may be transient, while completed metadata is persisted to system metadata and manifest files.

Dependencies and integration: includes `BulkLoading.h`, `FDBTypes.h`, and `fdbrpc.h`; integrates backup BulkDump snapshots and BulkLoad restore paths.

Risks: job range must contain task and manifest ranges. UID generation retries are bounded at 50 before `bulkdump_task_failed`. `getSubmitTime()` returns `now()` rather than a stored submit time, so it is diagnostic only.

Test signals: bulk dump job creation, range-task generation, manifest persistence, and backup snapshot-mode tests.
