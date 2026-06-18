# sources/storage-engines/tikv/components/tikv_util/src/metrics/process_dummy.rs

## Purpose
Provides the non-Linux no-op implementation of process metrics registration so cross-platform builds keep the same public API.

## Important APIs, Types, and Functions
- `monitor_process() -> std::io::Result<()>` returns `Ok(())` and registers nothing.

## Control Flow
There is no runtime control flow beyond immediate success.

## State and Persistence Behavior
No state is created or persisted.

## Dependencies and Integration Points
Selected by `metrics/mod.rs` under `#[cfg(not(target_os = "linux"))]` and exported as `monitor_process`.

## Risks
Non-Linux builds compile and run, but process metrics are absent. Callers must not assume metrics registration implies metric availability across all platforms.

## Test Signals
No tests; behavior is intentionally trivial.
