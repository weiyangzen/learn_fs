# sources/object-store/rustfs/crates/obs/src/metrics/collectors/dial9.rs

Purpose: provides telemetry for the dial9 Tokio runtime tracing subsystem itself. It always reports whether dial9 is enabled and conditionally reports event, bytes-written, rotation, error, CPU overhead, disk usage, and active session metrics.

Important APIs/types: `Dial9Stats`, `collect_dial9_metrics`, and `is_dial9_enabled`. Unlike most collectors in this directory, metrics are built with `PrometheusMetric::new` and hard-coded names rather than schema descriptors.

Control flow: `collect_dial9_metrics` reads the dial9 enabled flag via `is_dial9_enabled`, emits `rustfs_dial9_enabled`, and returns early when disabled. If enabled, it appends four counters and three gauges.

State/persistence: no stored state, but behavior depends on environment/config through `rustfs_config::{ENV_RUNTIME_DIAL9_ENABLED, DEFAULT_RUNTIME_DIAL9_ENABLED}` and `rustfs_utils::get_env_bool`.

Dependencies/integration: exported from `collectors/mod.rs`. It is not wired into the shown scheduler tasks, so integration likely depends on a separate dial9 runtime or future metrics task.

Risks: tests are environment-sensitive because detailed metric count depends on the enabled env/config value. Hard-coded metric descriptors bypass centralized schema, raising drift risk in naming/help/type conventions.

Test signals: tests cover default stat values, non-empty enabled flag output, and a value-populated path without asserting full count because dial9 may be disabled.
