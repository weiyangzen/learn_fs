# sources/security-integrity/cryfs/crates/e2e-perf-tests/Cargo.toml

## Purpose
Cargo manifest for the CryFS end-to-end performance test and benchmark crate.

## Important APIs, types, and functions
- Depends on CryFS blobstore, blockstore, config, filesystem, runner, rustfs, utils, and version crates.
- Uses Criterion with `async_tokio` for benchmarks.
- `benchmark` feature switches code paths from operation-count tests to mounted filesystem benchmarks.
- Registers `all_operations` bench with `harness = false`.

## Control flow
Normal `cargo test` builds the in-process operation-count harness. `cargo bench --features benchmark` enables mounted benchmark code and the Criterion main in `benches/all_operations.rs`.

## State and persistence behavior
The manifest itself stores no runtime state but selects whether temporary in-memory/tracked stores or real mounted benchmark paths are compiled.

## Dependencies and integration points
This crate is highly integrated with internal CryFS stack layers and FUSE/rustfs backends. It also depends on `nix`, `fuser`, `tokio`, `tempfile`, and logging utilities.

## Risks and edge cases
The crate depends on `cryfs-runner` despite a TODO saying it should not. Benchmark feature changes the compiled module set, so test and bench paths can diverge.

## Test signals
Cargo targets expose operation-count tests and Criterion benchmark execution; correctness expectations live in operation modules.
