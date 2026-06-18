# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskController.java

Purpose: `ReconTaskController` is the public controller contract for registering Recon OM tasks, feeding OM deltas, managing async task execution, and triggering reinitialization after buffer overflow or task failures.

Important APIs and types: `registerTask`, `consumeOMEvents`, `reInitializeTasks`, `getRegisteredTasks`, `start`, and `stop` define normal lifecycle. `hasEventBufferOverflowed`, `hasTasksFailed`, `queueReInitializationEvent`, `updateOMMetadataManager`, and test-visible `getEventBufferSize` support the newer async buffer and checkpoint reinitialization path. `ReInitializationResult` distinguishes successful queueing, retryable timing/checkpoint failures, and max retries.

Control flow and integration: OM sync code calls `consumeOMEvents`; upgrade actions and recovery paths call `queueReInitializationEvent`; controller implementation dispatches to `ReconOmTask` instances and updates status tables.

State and persistence: interface has no state, but it defines operations that change event buffer state, task failure flags, checkpoints, staged Recon DBs, and task status rows.

Dependencies: `OMMetadataManager`, `ReconOMMetadataManager`, `ReconTaskReInitializationEvent`.

Risks and test signals: implementations must handle concurrent event ingestion, backpressure, failure flags, and lifecycle shutdown. Tests should assert return semantics for reinit queueing and that `consumeOMEvents` does not process synchronously after async buffering is introduced.
