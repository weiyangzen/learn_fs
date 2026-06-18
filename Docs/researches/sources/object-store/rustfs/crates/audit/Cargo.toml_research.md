# sources/object-store/rustfs/crates/audit/Cargo.toml

## Purpose

This manifest defines the `rustfs-audit` library crate: an audit target management system for RustFS with multi-target fan-out, hot reload, observability, and replay/runtime integration.

## Important APIs and Types

The package uses workspace-managed edition, license, repository, rust-version, version, and homepage metadata. It disables doctests for the library. Runtime dependencies are the RustFS target abstraction, RustFS config with audit/constants/server-config-model features, S3 event types, async/concurrency crates, serialization, metrics, tracing, and Tokio. Dev dependencies provide async test traits, temporary environment helpers, and URL parsing.

## Control Flow

Cargo uses this manifest to compile the audit crate as a library. Feature selection is mostly delegated to workspace dependencies; the explicit Tokio features enable sync primitives, filesystem support, runtime flavors, time, and macros needed by the async audit system.

## State and Persistence

The manifest has no runtime state. It controls compile-time linkage to persistence-capable targets and replay stores through `rustfs-targets` and `rustfs-config`.

## Dependencies and Integration Points

The crate is tightly integrated with `rustfs-targets` for target plugins/runtime/replay, `rustfs-config` for audit target configuration, `rustfs-s3-types` for event names, `metrics` for metric emission, `tracing` for structured logs, and Tokio for async execution.

## Risks and Edge Cases

Because most versions and lints are workspace inherited, compatibility and MSRV risks sit at workspace level. Disabling doctests avoids doc example failures but also means public examples are not compiled. The audit crate depends on target/config feature flags; removing the `audit` or server config model features upstream would break this crate.

## Test Signals

Useful signals are `cargo check -p rustfs-audit`, unit/integration tests under `crates/audit/tests`, feature resolution against workspace dependencies, and lint enforcement through workspace lints.
