# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryUnifiedControl.java

Purpose: Tests queue-based unified control for triggering NSSummary tree rebuilds through `ReconTaskControllerImpl.queueReInitializationEvent`. It verifies that production callers can concurrently request rebuilds while a single async event-processing lane serializes actual `NSSummaryTask.reprocess` execution.

Important APIs and control flow: `setUp` resets static `NSSummaryTask` rebuild state, creates mocked Recon managers, configures an event buffer, registers a testable anonymous `NSSummaryTask`, wires checkpoint-capable `ReconOMMetadataManager`, and starts the controller. The overridden `executeReprocess` clears the namespace summary table, invokes dummy subtasks, and drives `RebuildState` transitions. Tests cover initial IDLE state, success, failure, retry after failure delay, concurrent queue attempts, `ReconUtils.getNSSummaryRebuildState`, exception recovery, checkpoint creation failure, and buffer integration.

State and persistence behavior: Focuses on in-memory static `RebuildState` (`IDLE`, `RUNNING`, `FAILED`) and controller event buffer state rather than durable Recon SQL data. Checkpoint mocks simulate DB snapshots used for rebuild isolation. Retry tests depend on the task/controller retry delay, using waits around 2100 ms.

Dependencies and integration points: Integrates `ReconTaskControllerImpl`, `ReconTaskReInitializationEvent`, `OMUpdateEventBuffer`, `ReconUtils`, `DBCheckpoint`, `DBStore`, `ReconOMMetadataManager`, and `ReconTaskStatusUpdaterManager`. The concurrency helper classes use `CountDownLatch`, `CompletableFuture`, and atomic counters to prove no concurrent rebuild execution.

Risks and test signals: High signal for concurrency serialization, retry gating, checkpoint failure behavior, and public state reporting. Risks include time-based sleeps that can be flaky on overloaded CI and reliance on static rebuild state reset in setup/teardown.
