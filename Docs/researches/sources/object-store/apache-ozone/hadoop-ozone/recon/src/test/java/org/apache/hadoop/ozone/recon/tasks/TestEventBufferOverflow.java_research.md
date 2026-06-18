# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestEventBufferOverflow.java

Purpose: This controller-level suite exercises Recon OM event buffer overflow handling, async reinitialization queueing, checkpoint retry behavior, and reset helpers introduced for non-blocking OM synchronization and reinitialization recovery.

Important APIs and types: It uses `ReconTaskControllerImpl`, `ReconTaskController.ReInitializationResult`, `ReconTaskReInitializationEvent.ReInitializationReason.BUFFER_OVERFLOW`, `OMUpdateEventBatch`, `ReconOmTask`, `ReconOMMetadataManager`, `DBStore`, `DBCheckpoint`, `ReconDBProvider`, task status DAOs/updaters, and manager mocks for container, namespace summary, global stats, and file metadata.

Control flow: Tests construct controllers with small `OZONE_RECON_OM_EVENT_BUFFER_CAPACITY` values, register mocked tasks, queue many synthetic OM event batches or explicit reinitialization events, and start the controller executor where needed. Latches coordinate reprocess start/completion. Checkpoint-failure tests spy `createOMCheckpoint` to throw and call `queueReInitializationEvent` repeatedly with sleep intervals to pass retry delay gates.

State and persistence behavior: SQL task-status DAO objects are real via `AbstractReconSqlDBTest`, but most Recon DB/OM DB state is mocked. Runtime state under test includes event-buffer size, overflow flag, dropped-batch count, tasks-failed flag, reinitialization retry counter, checkpoint paths, and controller executor lifecycle. `drainEventBufferAndCleanExistingCheckpoints` clears buffered events, while `resetEventFlags` clears overflow and task-failure flags.

Dependencies and integration points: The tests link the event ingestion path `consumeOMEvents` with reinitialization queueing, staged Recon DB provider access, checkpoint creation from the OM metadata manager, and task `reprocess` execution. They model fallback behavior expected by OM service-provider retry loops without standing up real OM snapshot transfer.

Risks: Several assertions are intentionally broad because async processing may or may not overflow depending on scheduling. Retry tests depend on fixed sleeps around the retry delay, which makes them slower and timing-sensitive. Heavy mocking means checkpoint cleanup, full snapshot fallback, and real DB checkpoint validity are only partially covered.

Test signals: Non-negative dropped batch counts, successful `queueReInitializationEvent`, latch-observed reprocess execution, `RETRY_LATER` for six checkpoint failures, `MAX_RETRIES_EXCEEDED` on the seventh attempt, `createOMCheckpoint` call count, empty buffer after drain/reset, and false overflow/tasks-failed flags after reset.
