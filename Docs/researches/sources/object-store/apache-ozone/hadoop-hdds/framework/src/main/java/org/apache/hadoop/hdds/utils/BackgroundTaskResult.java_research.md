# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskResult.java

Purpose: `BackgroundTaskResult` is the result contract returned by background tasks, mainly to report a result size for logging/metrics-like diagnostics.

Important APIs/types/functions: `getSize()` returns the number of entries represented by the result. Nested `EmptyTaskResult` provides `newResult()` and returns size `0`.

Control flow: `BackgroundService` logs `result.getSize()` at debug level after each task completes.

State and persistence: interface only; `EmptyTaskResult` instances are stateless but `newResult()` creates a new object each call.

Dependencies/integration: used by `BackgroundTask` and concrete services.

Risks: result size semantics are service-defined, so cross-service comparisons may be misleading. Returning null from a task would cause `BackgroundService` to throw/log when calling `getSize()`.

Test signals: background service tests use simple results to verify execution; component tests cover concrete result sizes indirectly.
