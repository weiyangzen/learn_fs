# sources/object-store/rustfs/crates/heal/Cargo.toml

## Purpose

This manifest defines the `rustfs-heal` crate, described as RustFS erasure set and object healing. It declares package metadata, workspace inheritance, dependencies, development dependencies, and disables doctests for the library target.

## Important APIs, Types, and Functions

As a Cargo manifest, it does not define Rust APIs directly. Its important interface is the crate package:

- Package name: `rustfs-heal`.
- Workspace-managed version, edition, license, rust-version, repository, homepage, and dependency versions.
- Description: `RustFS erasure set and object healing`.
- Library target with `doctest = false`.

## Control Flow

Cargo uses this file during dependency resolution and compilation. The selected dependencies enable async healing logic, storage access, admin/common/config integration, serialization, errors, metrics, and tests. Tokio is built with `sync`, `io-util`, `time`, and `macros` for normal use, and with `test-util` and `fs` in dev-dependencies.

## State and Persistence Behavior

No runtime state is stored here. The manifest controls build-time state: feature selection, dependency graph, package metadata, and documentation/test behavior. Disabling doctests means examples in crate docs, if any, will not be executed by `cargo test --doc`.

## Dependencies and Integration Points

Runtime dependencies include RustFS crates `rustfs-config`, `rustfs-ecstore`, `rustfs-storage-api`, `rustfs-common`, `rustfs-madmin`, and `rustfs-utils`; async/runtime crates `tokio`, `tokio-util`, `async-trait`, and `futures`; diagnostics/ops crates `tracing` and `metrics`; data/error crates `serde`, `serde_json`, `thiserror`, `anyhow`, and `uuid`.

Dev dependencies include `serial_test`, `tracing-subscriber`, `tempfile`, `walkdir`, `http`, `temp-env`, and extra Tokio features. These point to tests that likely exercise filesystem walks, temporary environments, HTTP-ish types, tracing setup, and serialized/isolated heal scenarios.

## Risks and Edge Cases

- `serde_json` appears in both dependencies and dev-dependencies; that is harmless but redundant unless different feature sets are needed.
- The crate uses both `thiserror` and `anyhow`, and `error.rs` has an `Anyhow` variant. Clear boundaries are needed to avoid losing typed error information.
- Healing is storage-critical; dependency changes in `rustfs-ecstore` or `rustfs-storage-api` can have broad impact.
- `doctest = false` reduces documentation test coverage.

## Test Signals

The manifest itself has no tests, but dev-dependencies indicate expected test coverage around temporary files/directories, serialized tests, environment manipulation, tracing, walking directory trees, HTTP types, and Tokio async testing.
