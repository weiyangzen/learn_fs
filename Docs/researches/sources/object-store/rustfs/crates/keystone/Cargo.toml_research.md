# sources/object-store/rustfs/crates/keystone/Cargo.toml

## Purpose
This manifest defines the `rustfs-keystone` crate, an OpenStack Keystone authentication integration for RustFS. It packages token validation, EC2 credential support, identity mapping, and Tower middleware into a reusable authentication crate.

## Important APIs, Types, and Functions
The manifest exposes a library crate named `rustfs-keystone` and registers one integration test target named `integration` at `tests/integration/mod.rs`. It depends on async/runtime and web middleware crates (`tokio`, `reqwest`, `tower`, `http`, `hyper`, `http-body`, `http-body-util`, `bytes`, `futures`), serialization/error/logging crates (`serde`, `serde_json`, `thiserror`, `tracing`, `time`, `moka`), and RustFS internal contracts (`rustfs-credentials`, `rustfs-policy`, `rustfs-utils`). Dev dependencies add `tower` utilities, `tokio` test utilities, and `temp-env`.

## Control Flow and Integration Points
The dependency graph matches the crate's main flow: environment config is loaded through `rustfs-utils`, Keystone HTTP calls are made with `reqwest`, validated identities are converted into `rustfs-credentials::Credentials`, roles map to `rustfs-policy`, and middleware plugs into Tower/Hyper request handling. The explicit integration test target centralizes tests through `tests/integration/mod.rs`.

## State and Persistence Behavior
The manifest itself has no runtime state. By enabling `moka`, `time`, and HTTP stack dependencies, it supports in-memory token caching and async Keystone API interactions implemented in source files.

## Dependencies
All dependencies are workspace-pinned. `hyper` is requested with `server`; middleware uses `http-body` and `http-body-util` to erase body types. `moka` is used for token caches. `temp-env` supports environment-driven configuration tests.

## Risks and Edge Cases
The manifest enables broad `tokio` features and `hyper` server features, which may increase compile surface for a focused auth crate. `reqwest` TLS behavior is controlled at runtime in `client.rs`; the manifest does not constrain TLS features here. Test coverage depends on the custom integration target and unit tests in modules.

## Test Signals
The `[[test]]` target ensures `tests/integration/mod.rs` runs as a single integration suite. Module-level unit tests exercise config parsing, identity mapping, middleware task-local storage, and token-to-credential conversion.
