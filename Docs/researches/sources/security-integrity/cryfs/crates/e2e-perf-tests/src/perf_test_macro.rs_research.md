# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/perf_test_macro.rs

## Purpose
This file provides the macro layer that expands compact performance scenario lists into either counter tests (`cargo test`) or Criterion benchmarks (`feature = "benchmark"`). It centralizes fixture selection, atime behavior variation, and group/benchmark naming.

## Important APIs, Types, and Functions
There are two cfg-gated `#[crabtime::function] fn perf_test_` definitions. In non-benchmark builds, `perf_test_` emits Rust modules and `#[test]` functions for every scenario, filesystem fixture, and atime behavior. In benchmark builds, it emits Criterion benchmark functions and a criterion group.

Public macro exports are `perf_test!`, `perf_test_only_fuser!`, and `perf_test_only_fusemt!`, which call `perf_test_!` with disable flags. `FixtureType` enumerates `FuserWithInodeCache`, `FuserWithoutInodeCache`, and `Fusemt`.

## Control Flow
At compile-time, crabtime receives the group name and list of scenario names. The non-benchmark branch builds a fixture list, iterates each test name, emits a `mod test_<normalized_name>`, and inside it emits one Rust `#[test]` per fixture and atime behavior. Each generated test constructs `TestDriverImpl` with `InMemoryBlockStore`, calls the scenario function, and runs `assert_op_counts`.

The benchmark branch emits one Criterion function per scenario, iterates atime behaviors inside each benchmark group, and conditionally benchmarks fuser or fuse-mt mounting drivers with `TempDirBlockStore`.

## State and Persistence Behavior
The file itself has no runtime persistence, but generated tests determine the blockstore type and fixture lifecycle. Counter tests use in-memory blockstores for deterministic action counts. Benchmarks use temporary directory blockstores and mounting drivers, so they exercise a more realistic persistence layer.

## Dependencies and Integration Points
This file depends on `crabtime`, `criterion`, `cryfs_blockstore`, `cryfs_rustfs::AtimeUpdateBehavior`, filesystem drivers, and `TestDriverImpl`. All operation files in `e2e-perf-tests/src/operations` integrate through these macros.

## Risks and Notes
Because this is compile-time code generation, syntax emitted as strings must remain valid Rust. `normalize_identifier` is duplicated between cfg branches. Fixture and atime matrices are hard-coded; adding a driver or atime behavior requires changing this file. Benchmark mode uses a reduced sample size of 10 with a TODO to revisit.

## Test Signals
The generated tests are the harness for all per-operation count assertions. The file's own signal is indirect: if macro expansion breaks, operation modules fail to compile or generated test names/groups disappear.
