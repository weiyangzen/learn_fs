# sources/storage-engines/tikv/components/tikv_util/src/metrics/threads_dummy.rs

## Purpose
Provides no-op non-Linux thread metrics and thread-info statistics so the utility API remains portable.

## Important APIs, Types, and Functions
- `monitor_threads(namespace)` returns `Ok(())`.
- `ThreadInfoStatistics::{new,record,get_cpu_usages,get_read_io_rates,get_write_io_rates}` are stubs returning empty maps.
- `Default` delegates to `new`.

## Control Flow
Methods perform no sampling and return immediately.

## State and Persistence Behavior
`ThreadInfoStatistics` has no fields and no persistent state.

## Dependencies and Integration Points
Selected by `metrics/mod.rs` on non-Linux targets and keeps callers source-compatible with Linux builds.

## Risks
Feature parity is intentionally absent. Components using thread CPU/IO maps must tolerate empty results on non-Linux systems.

## Test Signals
No tests; the primary signal is successful non-Linux compilation.
