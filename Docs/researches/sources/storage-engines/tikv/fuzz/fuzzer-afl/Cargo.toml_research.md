# sources/storage-engines/tikv/fuzz/fuzzer-afl/Cargo.toml

## Purpose
Defines the AFL-specific fuzzing crate used by the CLI to compile generated AFL harness binaries.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, and depends on `fuzz-targets`. On non-Windows x86_64 targets it adds the `afl` crate dependency.

## Control Flow
`fuzz/cli.rs` generates binaries into this package and runs `cargo afl build --bin <target>` followed by `cargo afl fuzz`.

## State and Persistence Behavior
No runtime state in the manifest. It controls dependency resolution and target-gated availability for AFL.

## Dependencies and Integration Points
Integrates with generated `src/bin/*.rs`, `template.rs`, the `fuzz-targets` crate, and the external `cargo afl` tool.

## Risks
AFL is only enabled for x86_64 non-Windows builds; other platforms may compile only the placeholder library. Edition 2024 requires a sufficiently new Rust toolchain.

## Test Signals
Run `cargo check -p fuzzer-afl` and an AFL pre-check on supported hosts. Verify generated binaries compile after target additions.
