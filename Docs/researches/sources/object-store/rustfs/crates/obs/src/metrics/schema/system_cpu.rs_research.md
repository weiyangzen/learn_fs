# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_cpu.rs

## Purpose
Defines host CPU metric descriptors for average idle, I/O wait, load, load percentage, nice, steal, system, and user time/usage.

## Important APIs, Types, and Functions
Exports eight no-label gauge descriptors under `subsystems::SYSTEM_CPU`, each backed by a `MetricName::SysCPU*` variant.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values. `collect_system_cpu_and_memory_stats()` builds `CpuStats` from a `sysinfo::System` snapshot, with some fields currently set to zero where sysinfo does not supply the exact Linux CPU time dimension.

## Dependencies and Integration Points
Used by `metrics/collectors/system_cpu.rs`. That collector also emits process CPU usage/utilization using descriptors from `system_process.rs`.

## Risks
Some descriptor names imply CPU time categories, but the current stats collector maps `system` to global CPU usage and `user`, `nice`, `steal`, `iowait` to zero. Consumers should treat these as best-effort until richer platform data is added.

## Test Signals
No local schema tests. Collector tests and stats-collector tests can verify stable output shape.
