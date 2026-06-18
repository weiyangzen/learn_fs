# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/NamedCallableTask.java

Purpose: `NamedCallableTask` wraps a `Callable` with a stable task name so asynchronous execution failures can be attributed to the Recon task that failed.

Important APIs and types: constructor stores `taskName` and `Callable<V>`. `getTaskName()` exposes the name. `call()` delegates directly to the wrapped callable.

Control flow and integration: `ReconTaskControllerImpl` creates these wrappers for both delta `process` calls and reprocess calls. When exceptions occur, the controller wraps them in `TaskExecutionException` with the same name and updates metrics and status for that task.

State and persistence: only holds an in-memory name and callable. Persistence is handled by controller status updates.

Dependencies: Java `Callable`.

Risks and test signals: null task names or callables are not checked. Tests should verify delegation, name retention, and exception propagation without swallowing checked exceptions.
