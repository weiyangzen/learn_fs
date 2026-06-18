# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskControllerIntegration.java

Purpose: This integration-style unit suite verifies that `ReconTaskControllerImpl.reInitializeTasks` cooperates with `NSSummaryTask`'s unified rebuild control. It focuses on static rebuild-state transitions, duplicate rebuild suppression, recovery after failure, and coexistence with other Recon tasks.

Important APIs and types: It uses `ReconTaskControllerImpl`, `NSSummaryTask`, `NSSummaryTask.RebuildState`, `ReconOmTask`, `TaskResult`, `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `OMMetadataManager`, `ReconDBProvider`, `DBStore`, task status updater mocks, `ExecutorService`, `CompletableFuture`, `CountDownLatch`, and `AtomicInteger`.

Control flow: `setUp` resets static NSSummary rebuild state, builds a testable anonymous `NSSummaryTask` that overrides `executeReprocess` with mocked sub-task callables, registers it plus a mock task in a started controller, and configures namespace-summary clearing to succeed by default. Individual tests use latches to hold rebuilds in `RUNNING`, invoke direct `reprocess` and/or controller `reInitializeTasks`, then release latches and inspect state and invocation counts.

State and persistence behavior: State is almost entirely mocked and in-memory. The critical state is static `NSSummaryTask` rebuild state moving between `IDLE`, `RUNNING`, and `FAILED`. The controller task registry and executor lifecycle are real. No real namespace summaries are persisted; `clearNSSummaryTable` is the mocked hook used to simulate rebuild work or failure.

Dependencies and integration points: The suite exercises the contract between task-controller reinitialization and NSSummary's global rebuild lock. It ensures other registered Recon tasks can still reprocess while NSSummary rebuild attempts are skipped or rejected due to an already-running rebuild.

Risks: Because `executeReprocess` is overridden, this does not validate actual FSO/Legacy/OBS rebuild logic. Static rebuild state makes isolation critical; `resetRebuildState` in setup and teardown is required. The concurrent test allows a range of call counts, which proves final state consistency more than exact suppression behavior. Shutdown behavior is timing-sensitive.

Test signals: `RUNNING` while a rebuild is blocked, `IDLE` after success, `FAILED` after simulated failure, recovery to `IDLE` on subsequent success, only one rebuild attempt during an external running rebuild, other-task reprocess counts, mixed success/failure tasks all attempted, and no final state stuck in `RUNNING` during shutdown.
