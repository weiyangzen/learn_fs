# sources/object-store/rustfs/crates/concurrency/src/lock.rs

## Purpose
Wraps core lock optimization with facade-level configuration, RAII guards, early release support, metrics, and tracing.

## Important APIs, types, and functions
`LockConfig` stores enablement and acquire timeout. `LockManager::new` creates `CoreLockOptimizer` with `LockOptimizeConfig`; accessors expose config, optimizer, stats, `optimize`, and enablement. `OptimizedLockGuard<G>` owns an optional underlying guard and can `early_release`. `LockScopeGuard<G>` is a minimal RAII wrapper.

## Control flow
Optimizing a guard calls `optimizer.on_acquire` and records whether optimization is enabled. Early release or drop takes the guard, computes hold time, calls `optimizer.on_release`, records lock hold time metrics, and logs release mode.

## State and persistence behavior
State is in memory: optimizer stats and guard-local acquisition time/release flag/resource string. There is no persisted lock state.

## Dependencies and integration points
Uses `rustfs_io_core::{LockOptimizer, LockStats}`, `rustfs_io_metrics::lock_metrics`, `tracing`, and caller-provided lock guard types such as mutex guards.

## Risks and edge cases
The manager ignores the separate `LockManagerPolicy` type and constructs `LockConfig` directly. Core options like max hold warning, adaptive spin, and max spin iterations are hard-coded. `as_ref` returns `None` after early release, so callers must handle optional access.

## Test signals
Tests create a manager and optimize a standard `Mutex` guard, then verify early release changes guard state.
