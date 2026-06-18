# sources/storage-engines/tikv/components/resource_metering/src/metrics.rs

## Purpose
`metrics.rs` declares Prometheus metrics for resource metering recorder/reporter activity.

## Important APIs, Types, And Functions
The file uses `lazy_static!` to register `STAT_TASK_COUNT`, `REPORT_DURATION_HISTOGRAM`, `REPORT_DATA_COUNTER` labeled by `type`, and `IGNORED_DATA_COUNTER` labeled by `type`.

## Control Flow
Metrics are registered at first use. Other modules increment stat task counts, observe reporting duration, count reported data, and count ignored data.

## State And Persistence Behavior
Metric state is global process state in Prometheus collectors. There is no local persistence.

## Dependencies And Integration Points
It depends on `lazy_static` and `prometheus`. Recorder and reporter modules consume these metrics to expose observability for collection and upload behavior.

## Risks
Registration uses `unwrap`, so duplicate metric names or registry failures panic during initialization. Metric names are global to the process and must stay unique.

## Test Signals
No local tests. Runtime metric registration and use are indirectly covered by recorder/reporter tests.
