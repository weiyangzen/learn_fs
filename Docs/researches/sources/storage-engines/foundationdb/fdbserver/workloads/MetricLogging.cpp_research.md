# sources/storage-engines/foundationdb/fdbserver/workloads/MetricLogging.cpp

## Purpose
Workload that exercises the `TDMetric` logging infrastructure by rapidly toggling boolean metrics or updating int64 metrics.

## Important APIs, types, and functions
`MetricLoggingWorkload` owns actor and metric counts, `testBool`, `enabled`, `changes`, `BoolMetricHandle` vector, and `Int64MetricHandle` vector. `setup` enables metric configs, `MetricLoggingClient` mutates metrics in batches, and metrics reporting exports changes and changes/sec.

## Control flow
Construction creates the requested metric handles. Setup waits two seconds then enables each metric's config. Start launches `actorCount` clients for `testDuration`. Each client loops forever, performing 100 metric updates per yield: boolean mode toggles the next metric modulo `metricCount`; int64 mode assigns the current change count.

## State and persistence behavior
No database state is used. State is in the process-wide metric subsystem and workload counters. `check` clears client futures and always succeeds.

## Dependencies and integration points
Depends on `flow/TDMetric.h`, tester workload scheduling, metric handle configuration, and perf counter export.

## Risks and test signals
The `enabled` option is read but not used to gate execution. High actor/metric counts can create high metric churn. Signals are absence of actor errors and the `Changes`/`Changes/sec` metrics.
