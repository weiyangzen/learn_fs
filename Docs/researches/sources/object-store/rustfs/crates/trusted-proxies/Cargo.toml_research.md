## sources/object-store/rustfs/crates/trusted-proxies/Cargo.toml

Purpose: declares the `rustfs-trusted-proxies` crate, which manages trusted proxy detection/ranges and middleware-related network security behavior.

Important APIs/types/functions: package metadata uses workspace versioning and lints, disables doctests, and declares two test targets: `unit_tests` at `tests/unit/mod.rs` and `integration_tests` at `tests/integration/mod.rs`.

Control flow and state: no runtime code. Dependencies include `async-trait`, `axum`, `http`, `ipnetwork`, `metrics`, `moka`, `reqwest`, `rustfs-config`, `rustfs-utils` net feature, serde, `thiserror`, Tokio, Tower, tracing, and regex. Dev dependencies add full Tokio/Tower utilities, `serial_test`, and `temp-env`.

Dependencies and integration points: cloud detector and metadata files depend on `reqwest`, `ipnetwork`, `async-trait`, Tokio, tracing, environment helpers, and app error types from this crate.

Risks: network metadata fetching depends on external cloud endpoints and public range JSON formats. `moka` cache and middleware dependencies indicate shared state/cache behavior elsewhere in the crate, not visible in this file.

Test signals: explicit unit and integration test targets suggest broader coverage outside this subset.
