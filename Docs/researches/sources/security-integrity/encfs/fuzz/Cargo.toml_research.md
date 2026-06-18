## sources/security-integrity/encfs/fuzz/Cargo.toml

Purpose: Cargo-fuzz manifest for EncFS fuzzing. It defines a separate fuzz package excluded from the main workspace and one libFuzzer target.

Important APIs and functions: package `encfs-fuzz`, `cargo-fuzz = true`, dependencies `libfuzzer-sys` with `arbitrary-derive`, `arbitrary`, path dependency on parent `encfs`, and `fuse_mt`. The `[[bin]]` target `fuzz_file_ops` points to `fuzz_targets/fuzz_file_ops.rs` and disables test/doc/bench.

State and persistence: Fuzz build outputs and corpus/crash artifacts under the fuzz project. Dependencies require nightly Rust per `rust-toolchain.toml` and cargo-fuzz. Integration is exposed by Taskfile `fuzz` and `fuzz-build`. Risks include API drift between `fuse_mt` versions in fuzz vs main package and fuzz-only dependency build failures.
