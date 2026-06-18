# sources/storage-engines/tikv/components/backup-stream/src/metadata/metrics.rs

## Purpose
`metadata/metrics.rs` registers Prometheus metrics for metadata operations, metadata watch events, and key-level operations in backup stream metadata code.

## Important APIs, types, and functions
- `METADATA_OPERATION_LATENCY` is a histogram vec labeled by operation type.
- `METADATA_EVENT_RECEIVED` is an event counter vec labeled by event type.
- `METADATA_KEY_OPERATION` is a counter vec for key operations, though the assigned source set does not show direct increments.

## Control flow
Metrics are lazily registered through `lazy_static!`. `MetadataClient` records operation latencies with `defer!` and increments event counters in `MetadataEvent::metadata_event_metrics`.

## State and persistence behavior
No durable state. The global Prometheus collectors are process-local observability state.

## Dependencies and integration points
Depends on `prometheus` and `lazy_static`. Integrated by `metadata/client.rs` and available inside the private `metadata` module.

## Risks and edge cases
- Metric names and label values are part of external observability contracts; renaming breaks dashboards and alerts.
- High-cardinality labels are avoided here by using operation/event type rather than task name.

## Test signals
No direct tests. Compile-time registration and use from `MetadataClient` provide basic coverage.
