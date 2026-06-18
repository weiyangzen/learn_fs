<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/metrics.rs -->
# sources/object-store/rustfs/crates/config/src/observability/metrics.rs

## Purpose
Defines the default system metrics scrape/collection interval and its environment key.

## Important APIs, types, and functions
`DEFAULT_METRICS_SYSTEM_INTERVAL_MS` is 30000 ms. `ENV_OBS_METRICS_SYSTEM_INTERVAL_MS` is `RUSTFS_OBS_METRICS_SYSTEM_INTERVAL_MS`.

## Control flow
No local logic; observability setup reads this for CPU/memory/disk/network collection cadence.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with system metrics collectors and observability exporters.

## Risks and edge cases
Too-low intervals can add system overhead; too-high intervals can hide short incidents. Parser bounds must be enforced downstream.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Metrics integration should verify interval override and collection cadence.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/metrics.rs -->
