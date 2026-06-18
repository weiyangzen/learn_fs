# sources/storage-engines/tikv/fuzz/targets/Cargo.toml

## Purpose
Defines the shared library crate containing actual fuzz target functions.

## Important APIs, Types, and Functions
Package `fuzz-targets` is unpublished, edition 2021, and uses `mod.rs` as its library path. It depends on `anyhow`, `byteorder`, `tidb_query_datatype`, and `tikv_util`.

## Control Flow
Fuzzer-specific generated binaries import functions from this crate. The root fuzz CLI also parses this crate's `mod.rs` to discover functions named `fuzz_*`.

## State and Persistence Behavior
No runtime persistence. The manifest defines compile-time dependencies and target layout.

## Dependencies and Integration Points
Integrates with all fuzzer templates, `fuzz/cli.rs` target discovery, TiKV codec utilities, and TiDB query datatype codecs.

## Risks
Changing the library path or crate name breaks templates and CLI discovery. Adding dependencies here affects all fuzzer builds.

## Test Signals
Run `cargo check -p fuzz-targets` and `cargo run -p fuzz -- list-targets` after adding/removing target functions.
