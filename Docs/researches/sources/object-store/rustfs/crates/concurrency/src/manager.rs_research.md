# sources/object-store/rustfs/crates/concurrency/src/manager.rs

## Purpose
Composes all feature-specific concurrency facades behind a single `ConcurrencyManager` and provides a small queue-utilization snapshot type for GetObject orchestration.

## Important APIs, types, and functions
`GetObjectQueueSnapshot` exposes `from_available_permits`, `permits_available`, `utilization_percent`, and `is_congested`. `ConcurrencyManager` stores `ConcurrencyConfig` and feature-gated `Arc` managers for timeout, lock, deadlock, backpressure, and scheduler. Constructors are `new`, `with_defaults`, and `from_env`; accessors and feature checks mirror enabled modules.

## Control flow
`new` validates config and panics if invalid, then builds each compiled feature manager from its policy. `start` starts deadlock monitoring only when the deadlock policy is enabled and logs feature status. `stop` stops the deadlock manager and logs shutdown.

## State and persistence behavior
Runtime state is in-memory manager arcs plus any state inside child managers. No config persistence or reload is implemented.

## Dependencies and integration points
Integrates all modules in the `rustfs-concurrency` crate and uses `tracing` for lifecycle events. Downstream services can keep one manager and pull subsystem managers as needed.

## Risks and edge cases
Invalid config causes a panic rather than a recoverable `Result`. Feature checks return config booleans, which can diverge from policy enablement and compile-time availability. `start` does not start scheduler/backpressure workers because those modules are passive facades.

## Test signals
Tests cover queue snapshot math, default manager creation, async lifecycle start/stop, and feature check calls.
