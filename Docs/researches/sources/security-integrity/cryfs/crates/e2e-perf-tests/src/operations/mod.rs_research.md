# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mod.rs

## Purpose
This module file is the registry for all operation-level e2e performance suites in the CryFS performance-test crate. It exposes each operation module so the crate can compile and macro-expand tests and benchmarks for filesystem operations such as `mkdir`, `open`, `read`, `readdir`, `readlink`, `release`, and `rename`.

## Important APIs, types, and functions
- Publicly declares operation modules with `pub mod ...` for chmod/chown/create/open/read/release/write and related filesystem calls.
- It does not define runtime functions or types; its API surface is the module export list.
- Contains cross-suite TODO notes describing desired future improvements to counter attribution, atime expectations, operation-count review, correctness checking, benchmark block sizes, and benchmark deadlock investigation.

## Control flow
There is no executable control flow in this file. Rust module loading makes the listed operation files part of the crate. Each child module owns its own `perf_test!` registration, so adding or removing an entry here directly controls whether that operation suite participates in compilation.

## State and persistence behavior
The file has no mutable state or persistence. Its indirect state impact is structural: exported modules instantiate tests and benchmarks that create isolated CryFS fixtures and tracking stores.

## Dependencies and integration points
This module is consumed by the crate root and by Rust's module system. It aligns operation modules with the `perf_test_macro` harness. The TODOs reference shared harness behavior, especially the fact that many operation measurements include an automatic flush/reset after the operation and currently do not split operation cost from flush cost.

## Risks and observations
The TODOs identify systemic risks across the suite. Atime behavior unexpectedly does not change many counts, even for operations that should update timestamps. Some benchmark runs may deadlock at startup. The file also suggests the suite is currently more performance-counter oriented than correctness oriented and would benefit from an `expect_output()` style harness.

## Test signals
Because this is a registry, its test signal is compile-time inclusion. A missing `pub mod` silently removes that operation suite from the crate. The comments provide important research context for interpreting all operation reports: exact counts may include forced cache flushing, may not fully distinguish atime paths, and may reflect known benchmark deadlock issues.
