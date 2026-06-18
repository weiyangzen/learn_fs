# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTask.java

Purpose: `BackgroundTask` is the callable unit executed by `BackgroundService`.

Important APIs/types/functions: extends `Callable<BackgroundTaskResult>` and narrows `call()` to return `BackgroundTaskResult`. `getPriority()` defaults to `0`; lower numeric values sort earlier in `BackgroundTaskQueue` because it uses `Comparator.comparingInt`.

Control flow: `BackgroundService` polls tasks from `BackgroundTaskQueue` and runs `call()` asynchronously. Result sizes may be logged for debugging.

State and persistence: interface only; implementations may hold service-specific state.

Dependencies/integration: used by all subclasses of `BackgroundService` and by `BackgroundTaskQueue`.

Risks: priority semantics are implicit; callers expecting larger values to run first would be wrong. Task exceptions are caught/logged by `BackgroundService` and do not stop the scheduler unless they are `Error`.

Test signals: `TestBackgroundService` uses tasks to verify scheduling; disk balancer and block deletion tests cover concrete task behavior.
