<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/config.rs -->
# sources/object-store/rustfs/crates/obs/src/config.rs

## Purpose
Builds RustFS observability configuration from environment variables. It covers OTLP endpoints and headers, signal enablement, profiling, stdout behavior, local rolling log settings, and cleaner retention/compression policy.

## Important APIs, Types, and Functions
`OtelConfig` is the main serializable/deserializable config struct. `OtelConfig::extract_otel_config_from_env` reads all env-backed settings and applies defaults. `OtelConfig::new` and `Default` call that function. `AppConfig` wraps `OtelConfig` for application-level config. `is_production_environment` checks the environment string against the production constant.

## Control Flow
An explicit endpoint argument takes priority over `RUSTFS_OBS_ENDPOINT`. If no endpoint is configured, `use_stdout` is forced true to preserve visible logs. Log directory is only set when the env var is non-empty. `log_keep_files` is normalized so zero falls back to the default. Profiling export reads a canonical env var with a legacy alias fallback.

## State and Persistence
The file stores no global state. It reads process environment each time config is constructed. Resulting config can drive telemetry setup and log cleaner scheduling.

## Dependencies and Integration
Depends heavily on `rustfs_config` constants and `rustfs_utils` env parsing helpers. `global::init_obs` and telemetry modules consume `OtelConfig`.

## Risks
Many fields are `Option<T>` even after defaults are applied, so downstream code must handle `None` for any manually constructed config. Sample TOML naming can drift from env-backed field names. Header parsing is not performed here, so invalid header strings fail later.

## Test Signals
Tests cover profiling export default disabled behavior, legacy alias support, and canonical env precedence over the legacy alias using a process-wide mutex to avoid env-test races.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/config.rs -->
