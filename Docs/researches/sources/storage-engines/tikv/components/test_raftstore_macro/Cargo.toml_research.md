# Research: sources/storage-engines/tikv/components/test_raftstore_macro/Cargo.toml

## sources/storage-engines/tikv/components/test_raftstore_macro/Cargo.toml

Purpose: crate manifest for the `test_raftstore_macro` procedural macro crate. It declares a private Apache-2.0 package on Rust 2021 and marks the library as `proc-macro = true`.

Important dependency choices are minimal and conventional for Rust macro generation: `proc-macro2` for token representation, `quote` for rendering, and `syn` with `full` plus `extra-traits` for parsing and comparing Rust syntax trees. There are no features, dev-dependencies, build scripts, or runtime dependencies.

Control flow and persistence behavior are Cargo-level only. The manifest integrates with the workspace as a test support crate and produces compiler plugin output consumed by tests using the attribute macro in `src/lib.rs`.

Risks are mostly version compatibility: this uses `syn` 1 APIs such as `attr.path`, so moving to `syn` 2 would require source changes. Because the crate is unpublished and private, its stability contract is internal to TiKV tests. Test signals are downstream compile-time macro expansion and the ability of crates using `#[test_case(...)]` to build generated tests.
