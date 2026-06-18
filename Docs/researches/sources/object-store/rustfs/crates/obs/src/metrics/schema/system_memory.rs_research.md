# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_memory.rs

## Purpose
Defines host memory metric descriptors for total, used, used percentage, free, buffers, cache, shared, and available memory.

## Important APIs, Types, and Functions
Exports eight no-label gauge descriptors under `subsystems::SYSTEM_MEMORY`, backed by `MetricName::Mem*` variants.

## Control Flow
Only lazy construction.

## State and Persistence
No values. `collect_system_cpu_and_memory_stats()` refreshes `sysinfo::System` memory data and maps it into `MemoryStats`. Buffers, cache, and shared are currently zeroed by the stats collector.

## Dependencies and Integration Points
Used by `metrics/collectors/system_memory.rs`, which also emits process resident/virtual memory descriptors from `system_process.rs`.

## Risks
Some fields are placeholders on the current sysinfo-based implementation, so dashboards must distinguish zero from actual kernel-reported zero. Units are bytes except `used_perc`.

## Test Signals
No direct tests. Collector-level tests can validate output shape; stats collector code is simple and indirectly covered by build/tests.
