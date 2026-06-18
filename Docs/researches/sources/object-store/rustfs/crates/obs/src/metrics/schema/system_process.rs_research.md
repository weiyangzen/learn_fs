# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_process.rs

## Purpose
Defines detailed process metrics under the system process subsystem: locks, CPU, runtime, file descriptors, process IO, syscalls, memory, process status, disk IO, and migrated process-level resource metrics.

## Important APIs, Types, and Functions
Exports many no-label descriptors. Counters include CPU total seconds, IO byte totals, and syscall totals. Gauges include locks, routine count, start time, uptime, descriptor limits/open count, resident/virtual memory, CPU usage/utilization, disk IO, and status. `PROCESS_STATUS_MD` encodes status as numeric categories.

## Control Flow
Only lazy descriptor construction. Runtime values are sampled from `snapshot_process_resource_and_system()` and converted in `collect_process_metric_bundle()`.

## State and Persistence
No values or persistence. Process metrics are process-lifetime snapshots/counters from OS and runtime sources.

## Dependencies and Integration Points
Used by `metrics/collectors/system_process.rs`, plus CPU, memory, drive, and GPU collectors import selected process-level descriptors for co-located output. It overlaps with `process_resource.rs` for simplified process resource metrics.

## Risks
`ProcessGoRoutineTotal` preserves a Go-oriented name even though this is RustFS; dashboards should understand it as a runtime task/thread equivalent only if collector semantics match. Numeric status codes need stable documentation. Some descriptors are gauges even for monotonic-looking values where OS snapshots may reset at process restart.

## Test Signals
Collector tests exercise process metric output. There are no schema-local tests for all names or type choices.
