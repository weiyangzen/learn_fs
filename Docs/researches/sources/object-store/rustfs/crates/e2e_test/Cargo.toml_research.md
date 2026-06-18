# sources/object-store/rustfs/crates/e2e_test/Cargo.toml

## Purpose
This manifest defines the RustFS `e2e_test` crate, a test-support and integration-test crate used to run S3, admin, protocol, checksum, compression, TLS, and cluster behavior tests against local RustFS binaries.

## Important APIs, Types, and Functions
The manifest enables optional features `ftps` and `sftp` plus an empty default feature set. It declares dependencies needed by the requested tests: AWS S3 SDK, `reqwest`, `tokio`, `serial_test`, `rustfs-signer`, `rustfs-madmin`, `rustfs-data-usage`, `rustfs-rio`, compression crates, hash crates, `zip`, `rcgen`, `rustls`, `clap`, and `anyhow`.

## Control Flow
The manifest controls test compilation and binary availability. The `src/bin/tls_gen.rs` binary is built from this crate and links to `e2e_test::tls_gen`. Test modules in `src/lib.rs` are gated by `#[cfg(test)]`, so they compile as integration-test support.

## State and Persistence
No runtime state is stored in the manifest. Dependencies enable tests to create temporary RustFS data directories, run child processes, generate TLS bundles, and serialize/deserialize admin responses.

## Dependencies and Integration Points
The crate integrates heavily with the workspace: `rustfs-config`, `rustfs-ecstore`, `rustfs-data-usage`, `rustfs-rio`, `rustfs-madmin`, `rustfs-filemeta`, and `rustfs-signer` are workspace crates. External dependencies provide S3 clients, HTTP clients, signing helpers, archive generation, TLS certificate generation, and async runtime support.

## Risks and Edge Cases
Because e2e tests spawn real RustFS binaries, dependency changes can affect compile time and runtime reliability. Optional protocol features must match binary build features through helper logic in `common.rs`. Tools like `awscurl` are external and skipped when absent in some tests.

## Test Signals
The manifest itself is not tested, but it is the dependency contract for all requested e2e files. Missing dependencies would break compilation of the corresponding modules or the `tls_gen` binary.
