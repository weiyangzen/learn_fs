# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/Cargo.toml

## Purpose
Defines the libFuzzer-specific fuzzing crate.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, depends on `fuzz-targets`, and includes `libfuzzer-sys = 0.3.1`.

## Control Flow
`fuzz/cli.rs` generates binaries from `template.rs` and runs `cargo run --target <platform> --bin <target> -- <corpus> <seeds>` with sanitizer coverage flags.

## State and Persistence Behavior
No runtime state in the manifest. It pins the crate-level libFuzzer integration used by generated binaries.

## Dependencies and Integration Points
Integrates with generated `src/bin` files, `fuzz-targets`, libFuzzer runtime, ASAN, and Linux/macOS targets selected in the CLI.

## Risks
`libfuzzer-sys` 0.3.1 and sanitizer flags may require nightly or specific host support. Unsupported OSes panic in the CLI before execution.

## Test Signals
Run `cargo check -p fuzzer-libfuzzer` and a short generated libFuzzer run on Linux/macOS. Verify sanitizer flags remain valid after Rust toolchain upgrades.
