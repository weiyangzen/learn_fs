# sources/storage-engines/tikv/cmd/tikv-ctl/build.rs

## Purpose
`cmd/tikv-ctl/build.rs` reuses the shared command build script for the `tikv-ctl` crate.

## Important APIs, types, and functions
It contains only `include!("../build.rs");`, so all behavior comes from `cmd/build.rs`: build time embedding and optional static C++ standard library link directives.

## Control flow
Cargo executes this build script for `tikv-ctl`; macro inclusion expands the parent build script at compile time.

## State and persistence behavior
It writes no files directly but causes `TIKV_BUILD_TIME` and linker instructions to be emitted by the included script.

## Dependencies and integration points
It depends on the parent `cmd/build.rs` remaining path-stable and on the `cc`/`time` build dependencies declared in `tikv-ctl/Cargo.toml`.

## Risks and edge cases
Relative include paths are fragile if the command directory layout changes. Debugging points to included code rather than local code.

## Test signals
`cargo build -p tikv-ctl` should execute the included script and show the same build-script behavior as other command crates using `cmd/build.rs`.
