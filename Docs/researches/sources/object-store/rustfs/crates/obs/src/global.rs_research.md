<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/global.rs -->
# sources/object-store/rustfs/crates/obs/src/global.rs

## Purpose
Provides crate-level observability initialization and global guard management. It also centralizes metric-name constants for log cleaner monitoring.

## Important APIs, Types, and Functions
`GLOBAL_GUARD` stores an `Arc<Mutex<OtelGuard>>` in a Tokio `OnceCell`. `OBSERVABILITY_METRIC_ENABLED` stores the one-time metrics-enabled flag. Public APIs include `observability_metric_enabled`, `init_obs`, `init_obs_with_config`, `set_global_guard`, and `get_global_guard`. Internal `set_observability_metric_enabled` logs when a conflicting second value is attempted.

## Control Flow
`init_obs` builds `AppConfig` from an optional endpoint and delegates to `init_obs_with_config`, which calls `telemetry::init_telemetry`. Setting the global guard logs initialization and fails if the cell is already set. Getting the guard returns `NotInitialized` when absent.

## State and Persistence
State is process-global and one-shot. Dropping the returned or stored `OtelGuard` controls telemetry flushing and shutdown, but this module itself does not persist anything.

## Dependencies and Integration
Uses config, error, telemetry initialization, Tokio `OnceCell`, tracing, and the metrics constants consumed by cleaner/core and dashboards. It is re-exported from crate `lib.rs`.

## Risks
Global one-time initialization can make repeated tests or embedded runtimes order-sensitive. `init_obs_with_config` returns a guard but does not set it globally; callers must explicitly call `set_global_guard` if global retrieval is needed. A mutex around guard shutdown can serialize access.

## Test Signals
Tests verify uninitialized guard errors, cleaner metric namespace prefixes, README/dashboard content for cleaner metrics, documented `init_obs_with_config` signature, and dashboard deployment references.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/global.rs -->
