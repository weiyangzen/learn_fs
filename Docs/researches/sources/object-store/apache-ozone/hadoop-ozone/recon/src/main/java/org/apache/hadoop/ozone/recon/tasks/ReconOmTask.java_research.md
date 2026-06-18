# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconOmTask.java

Purpose: `ReconOmTask` is the common contract for Recon tasks that consume OM metadata deltas and can rebuild themselves from a full OM metadata snapshot.

Important APIs and types: tasks implement `getTaskName`, `process(OMUpdateEventBatch, Map<String,Integer>)`, and `reprocess(OMMetadataManager)`. Optional hooks include `init()` and `getStagedTask(ReconOMMetadataManager, DBStore)`. The nested immutable `TaskResult` carries task name, subtask seek positions, and success. The builder defaults seek positions to an empty map.

Control flow and integration: `ReconTaskControllerImpl` registers task instances, wraps calls in `NamedCallableTask`, records task status, retries failed delta processing with returned subtask positions, and calls staged `reprocess` during reinitialization.

State and persistence: the interface itself has no state. Implementations persist through Recon managers and report sequence advancement through `TaskResult` plus status updater calls.

Dependencies: OM metadata manager, Recon OM metadata manager, DB store, Java maps.

Risks and test signals: task names are identity keys in maps and status rows, so they must be stable and unique. Failure results should include seek positions for restartable subtasks. Tests for implementations should cover init idempotence, staged task construction, delta retry with seek map, and full reprocess success/failure status.
