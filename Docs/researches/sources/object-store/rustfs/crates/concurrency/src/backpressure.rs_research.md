# sources/object-store/rustfs/crates/concurrency/src/backpressure.rs

## Purpose
Implements the concurrency-layer backpressure facade for duplex pipes and maps simple buffer/watermark policy into `rustfs-io-core` admission pressure monitoring.

## Important APIs, types, and functions
`PipeBackpressurePolicy` stores `buffer_size`, `high_watermark`, and `low_watermark` and computes byte thresholds plus `to_core_config`. `BackpressureManager` owns the policy, derived `CoreBackpressureConfig`, and shared `CoreBackpressureMonitor`. `BackpressurePipe` wraps Tokio `DuplexStream` endpoints and exposes reader/writer/split/state/age/meta/backpressure checks. `BackpressurePipeMeta` is the compact snapshot.

## Control flow
Constructing a manager derives core config and monitor. `create_pipe` creates a Tokio duplex stream using the configured buffer size and shares the monitor. `should_apply_backpressure` delegates to the core monitor and records a backpressure activation metric when true.

## State and persistence behavior
State is in memory: manager policy/config, an `Arc` monitor, pipe endpoints, and pipe creation time. There is no persisted configuration or queue state in this facade.

## Dependencies and integration points
Integrates `rustfs_io_core::{BackpressureConfig, BackpressureMonitor, BackpressureState}`, `rustfs_io_metrics::backpressure_metrics`, Tokio I/O duplex streams, and any I/O code that wants pipe-level flow control.

## Risks and edge cases
`to_core_config` hard-codes `max_concurrent = 32` and 100 ms cooldown, so facade users cannot tune those core dimensions. The policy itself does not validate high/low watermarks; validation happens in `ConcurrencyConfig`. Duplex buffer occupancy is not directly fed into the core monitor in this file, so correctness depends on how the monitor is updated elsewhere.

## Test signals
Unit tests check default policy shape, conversion to core watermarks, default manager state, and pipe metadata/state creation.
