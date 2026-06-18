<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/config.toml -->
# sources/object-store/rustfs/crates/obs/examples/config.toml

## Purpose
Provides an example observability configuration table for local use. It documents typical OTLP endpoint, stdout, sampling, metrics interval, service identity, environment, logger level, and local logging toggles.

## Important APIs, Types, and Functions
No executable API. The `[observability]` keys correspond to `OtelConfig` fields: `endpoint`, `use_stdout`, `sample_ratio`, `meter_interval`, `service_name`, `service_version`, `environments`, `logger_level`, and `local_logging_enabled`.

## Control Flow
No control flow. Consumers would parse the TOML into an application config, but the current `config.rs` primarily reads env variables rather than this file directly.

## State and Persistence
The file is static sample configuration. It does not alter runtime behavior unless explicitly loaded by an example or application.

## Dependencies and Integration
Acts as documentation for the observability crate and should stay aligned with `OtelConfig` env-backed fields and naming conventions.

## Risks
Some names appear older than current `OtelConfig` field names, such as `environments` versus `environment` and `local_logging_enabled` versus the current local logging fields. If users copy this file, stale keys may not be honored by current config loaders.

## Test Signals
No tests reference this TOML in the inspected files. Its value is mostly as operator-facing sample material.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/config.toml -->
