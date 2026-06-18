<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/Cargo.toml -->
# sources/object-store/rustfs/crates/obs/Cargo.toml

## Purpose
Declares the `rustfs-obs` crate metadata, features, and dependency graph for RustFS observability. The crate covers logging, metrics, tracing, runtime telemetry, profiling, and log cleanup.

## Important APIs, Types, and Functions
This TOML file has no Rust APIs, but it controls feature-gated availability. Default features are empty. `gpu` enables `nvml-wrapper`; `pyroscope` enables `jemalloc_pprof` and `pyroscope`. Platform-specific pyroscope dependencies are limited to macOS and Linux GNU x86_64.

## Control Flow
Cargo resolves workspace-shared dependencies and optional features. Tokio is enabled with runtime, sync, fs, time, and macros for library code, while dev-dependencies use full Tokio for examples/tests.

## State and Persistence
No runtime state. It influences build artifacts and dependency inclusion.

## Dependencies and Integration
Internal RustFS dependencies include audit, common, config, ecstore, iam, io-metrics, notify, security-governance, storage-api, and utils. External dependencies include OpenTelemetry, tracing, tracing-subscriber, tracing-appender, metrics, compression crates (`flate2`, `zstd`), sysinfo, crossbeam, glob, serde, and dial9 Tokio telemetry.

## Risks
The crate is broad and can pull substantial dependency weight when optional features are enabled. Feature compatibility across platform-specific profiling dependencies needs CI coverage. Workspace dependency versions must remain compatible across telemetry and metrics crates.

## Test Signals
`tempfile` and `temp-env` support filesystem and environment tests. The examples under `examples/` exercise configuration and dial9 integration paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/Cargo.toml -->
