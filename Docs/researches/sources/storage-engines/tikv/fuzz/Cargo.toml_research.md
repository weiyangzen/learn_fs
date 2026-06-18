# sources/storage-engines/tikv/fuzz/Cargo.toml

## Purpose
Defines the root fuzz CLI package. It builds the `fuzz` binary from `cli.rs` and supplies dependencies for target discovery, argument parsing, workspace metadata, regex scanning, lazy globals, and error handling.

## Important APIs, Types, and Functions
The package is unpublished, edition 2021, Apache-2.0 licensed. The `[[bin]]` entry names `fuzz` with path `cli.rs`. Dependencies are `anyhow`, `cargo_metadata`, `lazy_static`, `regex`, and `structopt`.

## Control Flow
Cargo uses this manifest to compile the CLI. The CLI then orchestrates fuzzer-specific child crates rather than this manifest directly building fuzz targets.

## State and Persistence Behavior
No runtime persistence. It fixes package metadata and dependency versions/requirements for reproducible local fuzz tooling.

## Dependencies and Integration Points
Integrates with the workspace, `fuzz/cli.rs`, and fuzzer subcrates under `fuzz/fuzzer-*`. `cargo_metadata` discovers workspace root; `regex` discovers functions in `targets/mod.rs`.

## Risks
Older `structopt`/`cargo_metadata` versions may lag current Cargo/clap behavior. If the CLI path or target discovery contract changes, this manifest must remain aligned.

## Test Signals
Run `cargo run -p fuzz -- list-targets` and `cargo check -p fuzz`. Dependency-audit checks should include this package even though it is unpublished.
