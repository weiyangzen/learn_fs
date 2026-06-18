# sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup_test.go

## Purpose

Verifies the reflection benchmark runner invokes setup, benchmark methods, and teardown exactly once per discovered benchmark method in the tested scenario.

## Important APIs, control flow, and dependencies

`benchmarkStructure` records counters for setup, teardown, and two benchmark methods. `BenchmarkRunBenchmarks` creates the struct, calls `benchmark_setup.RunBenchmarks`, and asserts the counters: two setup calls, one call to each benchmark method, and two teardown calls. The benchmark methods sleep for one second to reduce repeated invocations from benchmark calibration.

## State, persistence, dependencies, and integration points

The only state is in-memory counters on the benchmark struct. The test depends on Go benchmark execution behavior and testify assertions.

## Risks and test signals

Risk comes from benchmarking semantics: `b.N` and calibration can call benchmark bodies multiple times, so this test intentionally makes methods slow to stabilize counts. Signals are exact counter assertions showing per-sub-benchmark setup and cleanup execution.
