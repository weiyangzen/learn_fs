# sources/storage-engines/tikv/tests/benches/coprocessor_executors/mod.rs

## Purpose
This is the entry point for Criterion coprocessor executor benchmarks.

## Important APIs, Types, and Functions
It declares benchmark modules for hash aggregation, index scan, integrated DAGs, selection, simple aggregation, stream aggregation, table scan, top-N, and utilities. `execute` calls each module's `bench`. `run_bench` selects Criterion measurement backends: CPU time by default, Linux perf events when requested and compiled for x86_64 Linux, or wall time.

## Control Flow
`main` reads `TIKV_BENCH_MEASUREMENT`, builds an appropriate Criterion instance with `configure_from_args`, invokes all benchmark module registration, and prints the final summary.

## State and Persistence Behavior
No persistent state is owned. State is Criterion configuration and generated benchmark artifacts/profiles from lower-level benchers.

## Dependencies and Integration Points
It integrates the entire coprocessor executor bench tree and optional crates `criterion-cpu-time` and `criterion-perf-events`.

## Risks and Test Signals
Measurement backend selection is platform-sensitive. Unsupported measurement strings panic. Successful startup under the three supported measurement modes validates feature-gated dependencies and benchmark registration.
