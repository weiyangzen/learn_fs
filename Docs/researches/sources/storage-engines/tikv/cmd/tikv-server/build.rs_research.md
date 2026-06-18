# sources/storage-engines/tikv/cmd/tikv-server/build.rs

## Purpose
This build script delegates to the shared command-level build script by including `../build.rs`.

## Important APIs, Types, And Functions
The only active statement is `include!("../build.rs");`, so all build-time logic is centralized one directory up.

## Control Flow
During Cargo build, Rust expands the included build script contents as if they were in this file. That keeps `tikv-server` aligned with sibling command crates that share version/build metadata behavior.

## State And Persistence Behavior
Any emitted `cargo:` directives, environment-derived build metadata, or generated artifacts come from the included script, not from local logic.

## Dependencies And Integration Points
This file relies on the existence and compatibility of `cmd/build.rs` and the build dependencies declared in `Cargo.toml`.

## Risks And Edge Cases
The indirection makes local behavior invisible unless the included file is inspected. A path move or divergent binary-specific build need would require changing this include pattern.

## Test Signals
Compile/build-script execution in CI is the test signal. There are no direct unit tests.
