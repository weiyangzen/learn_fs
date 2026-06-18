# sources/object-store/rustfs/crates/concurrency/src/scheduler.rs

## Purpose
Implements adaptive I/O scheduling facade logic: policy conversion, priority selection, and multi-factor buffer sizing.

## Important APIs, types, and functions
`SchedulerPolicy` defines base/max buffer sizes and high/low priority thresholds with `to_core_config`. `SchedulerManager` owns the policy, derived `IoSchedulerConfig`, and `CoreIoScheduler`; it exposes scheduler access, strategy creation, `calculate_buffer_size`, and `get_priority`. `IoStrategy` applies media, access-pattern, load, and concurrency adjustments.

## Control flow
The manager builds a core scheduler from derived config. Buffer calculation creates an `IoSchedulingContext`, asks core scheduler for a base strategy using file size, a 10 ms permit wait, and sequential flag, applies facade adjustments, records a scheduler-decision metric, and caps at max buffer size.

## State and persistence behavior
State is in-memory policy/core scheduler data. Each calculation is stateless except for metrics emitted by `rustfs-io-metrics`.

## Dependencies and integration points
Uses `rustfs_io_core` scheduler, `IoLoadLevel`, `IoPriority`, `AccessPattern`, `StorageMedia`, and `rustfs_io_metrics::io_metrics`. Consumers are read/write paths that need dynamic buffer sizes and priority classes.

## Risks and edge cases
The constructed `IoSchedulingContext` is currently unused after creation. Multiplicative adjustments can reduce sizes substantially and are cast through `f64` to `usize`. `low_priority_threshold` can be lower than high threshold unless config validation is expanded. The 10 ms permit wait is hard-coded.

## Test signals
Tests validate default config ordering, policy-to-core mapping, high-priority classification for small size, and positive buffer-size calculation for SSD sequential low-load reads.
