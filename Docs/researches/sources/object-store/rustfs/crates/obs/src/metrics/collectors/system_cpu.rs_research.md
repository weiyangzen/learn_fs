# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_cpu.rs

Purpose: emits system CPU metrics and process CPU metrics. System metrics include average idle/iowait, load average, load percentage, nice, steal, system, and user percentages; process metrics include usage and utilization.

Important APIs/types: `CpuStats`, `ProcessCpuStats`, `collect_cpu_metrics`, and `collect_process_cpu_metrics`. Process collection accepts optional static-label slices, typically process PID/name labels from scheduler.

Control flow: `collect_cpu_metrics` returns eight descriptor-backed metrics. `collect_process_cpu_metrics` creates usage and utilization metrics, extends labels when supplied, and returns both.

State/persistence: stateless conversion. System data comes from `stats_collector::collect_system_cpu_and_memory_stats_with`; process CPU comes from `ProcessMetricBundle`.

Dependencies/integration: scheduler's system monitoring task emits system CPU at `system_interval` and process CPU at the same system-monitoring pass, while simple resource CPU is emitted at the resource interval.

Risks: process labels must remain low-cardinality; scheduler intentionally uses PID and executable name. CPU units and multi-core semantics differ between `usage` and `utilization`; consumers should read descriptor help.

Test signals: tests assert eight system CPU metrics with `rustfs_system_cpu_` prefix, default zeros, two process CPU metrics, values for usage/utilization, and label propagation.
