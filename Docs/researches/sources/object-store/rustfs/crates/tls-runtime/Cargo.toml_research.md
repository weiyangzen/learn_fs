## sources/object-store/rustfs/crates/tls-runtime/Cargo.toml

Purpose: declares the `rustfs-tls-runtime` crate, described as the project-wide TLS runtime foundation for RustFS.

Important APIs/types/functions: package metadata uses workspace version/edition/license/repository/rust-version/homepage, disables doctests for the library, and opts into workspace lints. Keywords and categories classify it as TLS/hot-reload/network-programming infrastructure.

Control flow and state: no runtime behavior, but dependencies shape the crate: `arc-swap` for atomic published state, `metrics`, `rustls` and `rustls-pki-types`, `serde`, `sha2`, `thiserror`, `tokio` with fs/rt/sync/time, and `tracing`.

Dependencies and integration points: consumed by `rustfs-targets` and likely server/global TLS initialization. Dev dependencies `rcgen`, `serde_json`, `tempfile`, and Tokio macros support local unit tests for certificates, status JSON, and async coordination.

Risks: choosing `aws_lc_rs` rustls crypto in code means runtime crypto-provider assumptions must match workspace rustls configuration. Disabling doctests avoids doc examples failing but also means public examples are not validated.

Test signals: this manifest enables focused unit tests across the crate but no integration tests are declared here.
