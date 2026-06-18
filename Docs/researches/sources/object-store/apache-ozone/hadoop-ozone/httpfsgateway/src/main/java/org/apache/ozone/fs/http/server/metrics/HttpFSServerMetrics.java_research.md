# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/metrics/HttpFSServerMetrics.java

## Purpose
`HttpFSServerMetrics` registers and exposes Hadoop Metrics2 counters for HttpFS server activity.

## Important APIs, Types, and Functions
The class is annotated `@Metrics(context = "httpfs")`. It tracks mutable counters for bytes written/read, write operations (`create`, `append`, `truncate`, `delete`, `rename`, `mkdir`), and read operations (`open`, `listing`, `stat`, `checkAccess`). `create(Configuration,String)` registers an instance with `DefaultMetricsSystem` and creates `JvmMetrics`. Increment methods update counters, getters expose values for tests/inspection, and `shutdown()` shuts down the default metrics system.

## Control Flow
`HttpFSServerWebApp.setMetrics()` calls `create()`, then operation executors in `FSOperations` increment counters during filesystem operations. `InputStreamEntity` or related streaming code is expected to update bytes read.

## State and Persistence Behavior
Metrics counters are in-memory and published through the Hadoop metrics system/JMX. No application data is persisted.

## Dependencies and Integration Points
It depends on HDDS metrics session ID configuration, Metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, mutable counters, and `JvmMetrics`. It is the metrics sink used by `FSOperations` and the webapp lifecycle.

## Risks and Edge Cases
Fields are populated by Metrics2 registration; direct construction without registration could leave counters null depending on Metrics2 injection behavior. `shutdown()` shuts down the global default metrics system, which can affect other metrics in the same JVM. Some HttpFS operations do not currently increment dedicated counters.

## Test Signals
The module contains a `TestHttpFSMetrics` file outside this assigned subset. In this subset, metrics are indirectly referenced by `FSOperations` and webapp initialization.
