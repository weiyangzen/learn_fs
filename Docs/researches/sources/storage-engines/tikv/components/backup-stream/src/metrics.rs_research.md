# sources/storage-engines/tikv/components/backup-stream/src/metrics.rs

## Purpose
`metrics.rs` defines backup stream Prometheus metrics and helper functions for task status gauges.

## Important APIs, types, and functions
- `TaskStatus` encodes `Running`, `Paused`, and `Error` as increasing integers.
- `update_task_status` sets a task status gauge, allowing escalation to higher states and always allowing reset to `Running`.
- `remove_task_status_metric` removes a task label from the hidden `TASK_STATUS` gauge vec.
- Registered metrics cover actor message duration, initial scan reasons/statistics/disk reads/size/duration, event handling stages, errors/fatal errors, heap memory, checkpoint ts, flush duration/file size, upload bytes, skip counters, stream enabled, observed regions, pending initial scans, min-ts resolve duration, temporary file memory/count/swap/read duration, smallest checkpoint, active subscriptions, and static miscellaneous event counters.

## Control flow
Metrics are registered lazily at process startup on first use. Runtime modules update them around endpoint task handling, event loading, router operations, temp-file management, checkpoint manager operations, and observer/subscription logic.

## State and persistence behavior
Metrics are process-local observability state exported through Prometheus. They do not persist backup data, but dashboards and alerts may rely on their names, labels, and monotonic/counter semantics.

## Dependencies and integration points
Depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`. It is imported by endpoint, errors, event loader, metadata, router, tempfiles, checkpoint manager, and observer-related code.

## Risks and edge cases
- Metric names and labels are an external compatibility surface for Grafana dashboards, as the file comment notes.
- `TaskStatus` uses max semantics across stores; incorrect reset or removal can mislead task-level status views.
- Some gauges are global rather than task-scoped, so concurrent tasks would need careful interpretation.

## Test signals
No direct tests. Compile-time metric registration and widespread runtime use provide integration coverage.
