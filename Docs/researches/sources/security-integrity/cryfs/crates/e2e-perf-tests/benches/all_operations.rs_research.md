# sources/security-integrity/cryfs/crates/e2e-perf-tests/benches/all_operations.rs

## Purpose
Criterion benchmark entry point aggregating all filesystem operation benchmarks when the `benchmark` feature is enabled.

## Important APIs, types, and functions
- Non-benchmark `main` panics with an instruction to enable the feature.
- Feature-gated `criterion_main!` lists benchmark groups from `cryfs_e2e_perf_tests::operations::*`.

## Control flow
Without `benchmark`, running the bench binary fails immediately. With the feature, Criterion dispatches every listed operation benchmark group, including both fuser/fuse-mt variants where defined.

## State and persistence behavior
No persistent state in this file; each benchmark group manages its own fixtures and temp stores.

## Dependencies and integration points
Connects the operation modules to Criterion's bench harness and enforces the feature-gated compilation model described by the crate root.

## Risks and edge cases
Adding a new operation module requires adding it here to be benchmarked. The panic path prevents accidental meaningless bench runs without the feature.

## Test signals
Criterion benchmark output across all listed filesystem operations.
