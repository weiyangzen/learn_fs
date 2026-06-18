# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/lib.rs

## Purpose
Crate root documenting and wiring the CryFS end-to-end performance test/benchmark harness.

## Important APIs, types, and functions
- `#![cfg(any(test, feature = "benchmark"))]` prevents normal library use.
- Modules: `env_logger` in non-benchmark mode, `filesystem_driver`, `filesystem_fixture`, public `operations`, `perf_test_macro`, `test_driver`, and `utils`.
- Compile-time version assertion through `cryfs_version`.

## Control flow
Compilation is mode-dependent: tests use in-memory/tracked APIs and operation-count assertions, while benchmark feature compiles mounted syscall drivers and Criterion benches.

## State and persistence behavior
No root state; submodules own temporary stores and counters.

## Dependencies and integration points
This is the public surface consumed by `benches/all_operations.rs` and by cargo tests generated from operation modules.

## Risks and edge cases
The crate is unavailable outside tests/benchmark feature by design. Feature-dependent module inclusion can hide compile failures in the other mode.

## Test signals
Successful `cargo test` and `cargo bench --features benchmark` compilation/execution validate the root wiring.
