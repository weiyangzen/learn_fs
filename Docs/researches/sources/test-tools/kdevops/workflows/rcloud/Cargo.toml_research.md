<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Cargo.toml -->
# sources/test-tools/kdevops/workflows/rcloud/Cargo.toml

## Purpose
This manifest defines the `rcloud` Rust package, a kdevops private-cloud REST API server that exposes VM lifecycle operations over libvirt. It builds a single binary named `rcloud` from `src/main.rs`.

## Important Dependencies
Core runtime dependencies are `actix-web` and `actix-rt` for HTTP service, `tokio` with full features for async runtime support, `serde`, `serde_json`, and `serde_yaml` for API and kdevops configuration data, `virt` for libvirt bindings, `tera` for XML templating support, `tracing` plus `tracing-subscriber` and `tracing-actix-web` for logs, `prometheus-client` for metrics, `anyhow` and `thiserror` for error handling, `uuid` for VM IDs, and `chrono` for time support. `clap` is optional behind the `cli` feature.

## Control Flow and Integration
The package metadata sets edition 2021, minimum Rust 1.70, and points repository/license metadata back to kdevops. The `Makefile` in the same workflow calls `cargo build --release` in this directory, and the generated binary is installed by the kdevops rcloud Ansible workflow.

## State and Persistence
The manifest itself does not persist runtime state, but it controls the dependency lock and binary build graph. Persistent VM state is delegated to libvirt and disk files in the Rust code.

## Risks and Test Signals
The `virt` crate requires system libvirt headers and libraries, which the workflow Makefile checks with `pkg-config`. `config`, `thiserror`, `tera`, and `chrono` are not heavily used in the current code, which may indicate planned features or dependency drift. Test signals are `cargo test`, health endpoint integration tests, and successful release builds under the kdevops Makefile target.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Cargo.toml -->
