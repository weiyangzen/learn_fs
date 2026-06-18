# sources/security-integrity/cryfs/crates/cryfs-runner/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-runner` crate, which assembles mounting, daemonization, IPC, filesystem construction, and integration-test helper binary dependencies.

## Important APIs, types, and functions
- Package metadata inherits workspace authors, edition, rust-version, license, repository, readme, and version.
- Runtime dependencies include `cryfs-filesystem`, `cryfs-config`, `cryfs-rustfs` with `fuser`, blobstore/blockstore crates, CLI utilities, `interprocess`, `postcard`, `tokio`, `tokio-util`, `serde`, `libc`, `nix`, and `command-fds`.
- Dev dependencies add `nix` process/signal features and `tempfile`.
- Defines `cryfs-runner-test-background` binary at `src/bin/cryfs_runner_test_background.rs`.

## Control flow
The manifest controls feature wiring and test binary availability rather than runtime flow. The helper binary is always buildable for integration tests because `required-features = []`.

## State and persistence behavior
No direct state. Dependency choices determine runtime persistence through block/blob/filesystem crates and daemon IPC serialization with postcard.

## Dependencies and integration points
This crate is the junction between the filesystem crate, RustFS/FUSE backend, config/local-state handling, blockstore integrity callbacks, IPC pipes, and logging configuration.

## Risks and edge cases
`cryfs-rustfs` disables default features and enables `fuser`, so backend behavior depends on that feature set. `command-fds` relies on pre-exec fd mapping until a future stdlib fd API exists. Serialization compatibility depends on serde/postcard versions across parent and daemon binaries.

## Test signals
`cargo test -p cryfs-runner` should build the helper binary and integration tests. Dependency feature regressions usually surface as compile errors or missing `CARGO_BIN_EXE_cryfs-runner-test-background`.
