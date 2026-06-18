# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/DataNodeMetricsService.java

## Purpose
`DataNodeMetricsService` asynchronously collects pending-deletion metrics from all datanodes, aggregates totals, tracks failures, and serves the latest collection status/results to API callers.

## Important APIs, Types, And Functions
It is a singleton service injected with Recon SCM, configuration, and `MetricsServiceProviderFactory`. Public methods are `startTask()`, `getCollectedMetrics(Integer)`, and `shutdown()`. Internal flow uses `CollectionContext`, `MetricCollectionStatus`, `submitMetricsCollectionTasks`, `processCollectionFutures`, `checkAndHandleTimeout`, `handleCompletedFuture`, and `updateFinalState`.

## Control Flow
`getCollectedMetrics` calls `startTask`. `startTask` prevents concurrent runs with `isRunning`, enforces a minimum delay since last completion, handles empty datanode lists, sets status in progress, and schedules `collectMetrics`. Collection submits one `DataNodeMetricsCollectionTask` per node, polls futures every 200 ms, cancels tasks after the configured timeout, accumulates successful pending-byte counts, records failures with `-1`, sorts results descending, and publishes final state.

## State And Persistence
State is in-memory: current status, result list, totals, failure counts, last collection time, and executor. No metrics are persisted by this class.

## Dependencies And Integration Points
It depends on `ReconNodeManager`, `DatanodeInfo`, HTTP policy, DN metrics config keys, `MetricsServiceProviderFactory`, `DataNodeMetricsCollectionTask`, and `DataNodeMetricsServiceResponse`.

## Risks
State fields are not all volatile and reads are not synchronized in `getCollectedMetrics`, so callers may observe stale values. The same executor runs the async orchestrator and per-node tasks, so a pool of size one can deadlock/starve. Timeout is measured from batch submission time, not per-task start. Failed placeholder results sort with negative values last.

## Test Signals
Tests should cover concurrency guard, rate limiting, empty-node handling, success aggregation, failed task counting, timeout cancellation, limit slicing, status transitions, executor shutdown, and low thread-count behavior.
