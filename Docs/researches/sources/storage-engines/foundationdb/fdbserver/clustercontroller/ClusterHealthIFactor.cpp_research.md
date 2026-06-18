# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.cpp

## Purpose

`ClusterHealthIFactor.cpp` implements the concrete cluster-health factors. Each factor reads latest worker trace events through `IWorkerEventProvider` and returns a `cluster_health::Level`.

## Important APIs, Types, and Functions

- `filterEmptyEvents()` drops empty `TraceEventFields` so role-filtered checks ignore stale/non-role workers.
- `fetchSpaceLevel()` handles shared disk-space threshold evaluation and missing/parse-failure behavior.
- `StorageSpaceFactor` reads `StorageMetrics` fields `KvstoreBytesAvailable` and `KvstoreBytesTotal`.
- `TLogSpaceFactor` reads `TLogMetrics` fields `QueueDiskBytesAvailable` and `QueueDiskBytesTotal`.
- `StorageReplicationFactor` reads `MovingData` counters and maps zero replicas to `OUTAGE`, critical one-replica policy to critical, repairs to `SELF_HEALING`, and clean data to `HEALTHY`.
- `RecoveryStateFactor` maps recovery progress to outage, self-healing, or healthy.
- `ProcessErrorsFactor` treats latest process errors as critical and successful empty responses as healthy.
- `RkThrottlingFactor` maps zero TPS limit to outage and low `TPSLimit / ReleasedTPS` ratio to critical.

## Control Flow

Factor methods are Flow coroutine futures. They fetch provider data, filter/parse expected fields, return severity, and convert missing telemetry or parsing errors into `METRICS_MISSING` with warning traces. `CODE_PROBE` branches instrument simulation coverage.

## State and Persistence Behavior

Factors are stateless except constructor thresholds for disk-space and ratekeeper checks. They do not cache or persist metrics.

## Dependencies and Integration Points

The file depends on `RecoveryState`, `TraceEventFields`, Flow futures, `CODE_PROBE`, and `ClusterHealthMonitor.h`. `Monitor::run()` calls these factors and logs their results.

## Risks

Exact trace-event and field names are required. Telemetry drift maps to `METRICS_MISSING`, which can obscure real incidents. Role-specific provider paths must remain current to avoid reading stale all-worker events.

## Test Signals

`ClusterHealthMonitorTesting.cpp` covers healthy, intervention, critical, outage, self-healing, role-filtering, partial failure, idle ratekeeper, and missing-metric cases.
