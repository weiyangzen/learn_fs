# sources/object-store/rustfs/crates/concurrency/src/timeout.rs

## Purpose
Provides timeout policy conversion, adaptive timeout calculation, async operation wrapping, and manual cancellation guards for the concurrency facade.

## Important APIs, types, and functions
`TimeoutManagerPolicy` carries default/max/min timeout and dynamic enablement, with `to_core_config`. `TimeoutManager` exposes constructors, config/core-config accessors, `calculate_timeout`, `wrap_operation`, and `create_guard`. `TimeoutGuard` exposes elapsed timeout checks, remaining time, cancellation token cloning, and cancellation.

## Control flow
`new` derives `min_timeout` from default/max. `from_policy` clamps min to max before deriving core config. `calculate_timeout` returns default timeout when dynamic mode is disabled, otherwise calls `calculate_adaptive_timeout` and clamps to min/max. `wrap_operation` delegates to `tokio::time::timeout` and normalizes elapsed timeout to `TimeoutError::TimedOut`.

## State and persistence behavior
Manager state is immutable in memory. `TimeoutGuard` stores start time, timeout, and a `CancellationToken`; it does not spawn tasks or persist progress.

## Dependencies and integration points
Uses `rustfs_io_core::{TimeoutConfig, TimeoutError, calculate_adaptive_timeout}`, Tokio timeouts, and `tokio_util::sync::CancellationToken`. I/O operations can use either wrapping or cooperative cancellation.

## Risks and edge cases
The `history` argument to `calculate_timeout` is unused. `timeout_per_mb` is set to zero in core config, so adaptive behavior depends entirely on `calculate_adaptive_timeout` defaults. Wrapped futures must map errors into `TimeoutError`. Cancellation guards require callers to observe the token.

## Test signals
Tests cover default policy ordering, policy-to-core mapping, min-timeout sanitization for small max values, successful wrapped operations, and adaptive clamp behavior.
