# sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/Cargo.toml

## Purpose
Defines the Honggfuzz-specific fuzzing crate used by the CLI.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, and depends on `fuzz-targets`. On non-Windows targets it depends on `honggfuzz = 0.5.47`.

## Control Flow
`fuzz/cli.rs` generates binaries into this package, sets sanitizer and `HFUZZ_RUN_ARGS`, and runs `cargo hfuzz run <target>`.

## State and Persistence Behavior
No runtime state in the manifest; it provides dependency and package metadata for generated harnesses.

## Dependencies and Integration Points
Integrates with `fuzzer-honggfuzz/template.rs`, `fuzz-targets`, and the external `cargo hfuzz` command.

## Risks
Windows is excluded. Honggfuzz version/toolchain compatibility matters, and edition 2024 requires modern Rust.

## Test Signals
Run `cargo check -p fuzzer-honggfuzz` and `cargo hfuzz version`. Compile a generated target after changing fuzz target signatures.
