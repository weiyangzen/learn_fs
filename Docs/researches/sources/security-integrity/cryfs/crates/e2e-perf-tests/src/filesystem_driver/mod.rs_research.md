# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mod.rs

## Purpose
Filesystem driver module aggregator and feature-gated export point.

## Important APIs, types, and functions
- Re-exports `FilesystemDriver`.
- Non-benchmark exports: `FuserFilesystemDriver`, `WithInodeCache`, `WithoutInodeCache`, and `FusemtFilesystemDriver`.
- Benchmark exports: `FusemtMountingFilesystemDriver` and `FuserMountingFilesystemDriver`.

## Control flow
Compile-time `cfg(feature = "benchmark")` selects mounted drivers for benchmarks or in-process drivers for operation-count tests.

## State and persistence behavior
No state.

## Dependencies and integration points
Connects crate features to the fixture/test-driver code that chooses concrete driver types.

## Risks and edge cases
Feature-gated module sets mean code can compile in test mode but fail in benchmark mode, or vice versa.

## Test signals
Compilation under both default test and benchmark features is the direct signal.
