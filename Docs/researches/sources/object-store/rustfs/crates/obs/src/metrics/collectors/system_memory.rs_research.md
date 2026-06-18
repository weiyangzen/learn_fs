# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_memory.rs

Purpose: emits system memory metrics and process memory metrics.

Important APIs/types: `MemoryStats` includes total, used, used percentage, free, buffers, cache, shared, and available bytes. `ProcessMemoryStats` includes resident and virtual memory. Exported collectors are `collect_memory_metrics` and `collect_process_memory_metrics`.

Control flow: system memory returns eight descriptor-backed metrics. Process memory creates resident and virtual metrics and extends optional labels.

State/persistence: stateless conversion. Values are sourced from sysinfo-backed collection in `stats_collector` and process metric bundles.

Dependencies/integration: scheduler's system monitoring task emits system memory with CPU/network/disk process metrics and labels process memory with PID/name.

Risks: Linux memory concepts such as buffers/cache/shared/available may vary by platform and sysinfo behavior. There is overlap between process memory metrics emitted here and full process stats in `system_process.rs`, so descriptor naming must avoid duplicate incompatible samples.

Test signals: tests assert eight system metrics with `rustfs_system_memory_` prefix, default zeros, two process memory metrics, and optional label propagation.
