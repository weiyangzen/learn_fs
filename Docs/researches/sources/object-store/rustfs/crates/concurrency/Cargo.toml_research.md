# sources/object-store/rustfs/crates/concurrency/Cargo.toml

## Purpose
Defines the `rustfs-concurrency` crate, a feature-gated facade for timeout, lock, deadlock, backpressure, and scheduler behavior used by RustFS I/O paths.

## Important APIs, types, and functions
The manifest enables default features `timeout`, `lock`, `deadlock`, `backpressure`, and `scheduler`. It depends on internal crates `rustfs-io-core` and `rustfs-io-metrics`, `tokio` with sync/time/rt, `tokio-util`, `thiserror`, and `tracing`.

## Control flow
Compile-time feature selection controls which modules in `src/lib.rs` are built and re-exported. Docs.rs is configured to build all features.

## State and persistence behavior
No runtime state is defined in the manifest. The relevant behavior is build-time dependency and feature resolution.

## Dependencies and integration points
This crate is the business-layer wrapper around shared I/O algorithms and metrics. Downstream crates import the facade while the manifest keeps reusable algorithms in `io-core` and instrumentation in `io-metrics`.

## Risks and edge cases
Default-enabling every feature means most consumers pay for all facade modules unless they opt out. Feature-dependent imports in `config.rs` assume the corresponding modules are available, so non-default feature combinations need compile coverage. Tokio dev features support tests only.

## Test signals
Manifest-level validation is indirect through `cargo test`/`cargo check` across feature combinations and docs.rs all-feature builds.
