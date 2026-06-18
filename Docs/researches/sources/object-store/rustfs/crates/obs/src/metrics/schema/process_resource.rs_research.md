# sources/object-store/rustfs/crates/obs/src/metrics/schema/process_resource.rs

## Purpose
Defines a small legacy/simple process-resource schema for CPU percent, resident memory bytes, and uptime seconds under a custom `/process` subsystem.

## Important APIs, Types, and Functions
Exports `PROCESS_CPU_PERCENT_MD`, `PROCESS_MEMORY_BYTES_MD`, and `PROCESS_UPTIME_SECONDS_MD`, all gauges with no labels and `MetricName::Custom` suffixes.

## Control Flow
Only lazy descriptor initialization.

## State and Persistence
No state. Values are populated by `collect_process_stats()` from `snapshot_process_resource_and_system()`.

## Dependencies and Integration Points
Used by `metrics/collectors/resource.rs`. It overlaps with richer descriptors in `system_process.rs`, which include CPU total, memory, IO, status, and descriptor counts.

## Risks
Custom names and custom subsystem mean this schema sits outside the strongly enumerated subsystem set. Overlap with system process metrics can produce parallel names with similar semantics but different metric families.

## Test Signals
Resource collector tests check representative metric names and values. No schema-local tests exist.
