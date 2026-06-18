# File Research: sources/virtualization/nbdkit/plugins/rust/cargo-tests.sh

Test wrapper for the Rust crate. It sources the repository test helpers, enables shell tracing and exit-on-error, sets `RUSTFLAGS=-Dwarnings`, then runs `cargo test --all-features` in both debug and release modes.

This catches warnings as hard failures and exercises optional feature coverage, including the `nix`-gated APIs.
