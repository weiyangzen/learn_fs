# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTask.java

Purpose: Top-level `ReconOmTask` that rebuilds and incrementally maintains Recon namespace summaries for FSO, Legacy, and OBS bucket layouts.

Important APIs/types: `RebuildState`, `BucketType`, constructor wiring of three subtasks, `getStagedTask`, `process`, `reprocess`, `executeReprocess`, `buildTaskResult`, and test hooks for rebuild state.

Control flow and persistence: incremental `process` runs FSO, Legacy, and OBS processors in a static three-thread executor, each with its own seek position. It returns a `TaskResult` carrying updated subtask seek positions. Reprocess uses a static `AtomicReference` to prevent concurrent rebuilds, clears the namespace summary table, and invokes the three reprocess subtasks in parallel. Success resets state to IDLE; failures set FAILED.

Dependencies and integration: depends on `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `OzoneConfiguration`, and config keys for flush thresholds and parallelism. Upgrade actions and endpoints inspect rebuild state through test-visible/static paths.

Risks: static executor is never shut down. Returning success when another thread is already rebuilding may hide skipped work from callers expecting this invocation to rebuild. FAILED state can be retried because compare-and-set uses current state, but callers must know this behavior. Clear plus parallel rebuild means subtask ordering must ensure parent summaries exist when needed.

Test signals: `TestNSSummaryUnifiedControl`, tree precompute tests, and endpoint tests cover much of this. Add coverage for subtask seek-position recovery, duplicate rebuild request semantics, and executor failure behavior.
