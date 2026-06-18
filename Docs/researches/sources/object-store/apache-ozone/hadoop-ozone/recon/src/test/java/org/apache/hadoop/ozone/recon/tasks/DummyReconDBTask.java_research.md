# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/DummyReconDBTask.java

Purpose: This test helper implements `ReconOmTask` with deterministic pass/fail behavior. It lets controller tests model tasks that always pass, fail once, or always fail without needing a real OM table processor.

Important APIs and types: The class implements `ReconOmTask` methods `getTaskName`, `getTaskTables`, `process`, and `reprocess`, and exposes enum `TaskType` with `ALWAYS_PASS`, `FAIL_ONCE`, and `ALWAYS_FAIL`. It returns `volumeTable` from `getTaskTables` and uses `buildTaskResult` from the interface default/helper contract.

Control flow: The constructor sets `numFailuresAllowed` to `1` for `FAIL_ONCE`, `Integer.MAX_VALUE` for `ALWAYS_FAIL`, and leaves it at `Integer.MIN_VALUE` for `ALWAYS_PASS`. Both `process` and `reprocess` increment `callCtr` and return failure while the counter is within the allowed failure count, otherwise success.

State and persistence behavior: State is in-memory only: `taskName`, `callCtr`, and `numFailuresAllowed`. There is no database access despite the name. Reusing one instance across operations intentionally makes process/reprocess outcomes depend on prior calls.

Dependencies and integration points: It is intended for Recon task controller tests that need predictable retry and failure behavior for `OMUpdateEventBatch` processing and full reprocess. Its `volumeTable` declaration ties it to the controller's table-filtering expectations.

Risks: `ALWAYS_PASS` relies on the sentinel `Integer.MIN_VALUE`, which is terse but non-obvious. The class is package-private through its constructor, so it is mainly usable inside the task test package. Because process and reprocess share one counter, a mixed test can accidentally consume the one allowed failure in a different phase than intended.

Test signals: Consumers observe `TaskResult.isTaskSuccess()` transitions and count calls to validate retry, ignore, or reinitialization behavior.
