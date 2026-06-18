# sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup.go

## Purpose

Provides a small reflection-based benchmark runner for integration benchmark suites. It discovers methods named `Benchmark*` on a struct, runs each as a sub-benchmark, and wraps each benchmark with setup and teardown hooks.

## Important APIs, control flow, and dependencies

`Benchmark` requires `SetupB(*testing.B)` and `TeardownB(*testing.B)`. `getBenchmarkFunc` looks up a named method on a reflected value and verifies it has signature `func(*testing.B)`, failing the benchmark immediately if not. `RunBenchmarks` iterates `reflect.TypeOf(x).NumMethod`, filters names with `strings.HasPrefix("Benchmark")`, and calls `b.Run` with `b.Cleanup` registered before `x.SetupB` and benchmark execution.

## State, persistence, dependencies, and integration points

No persistent state is owned by this utility. It coordinates suite-local benchmark resources by guaranteeing teardown registration even if setup or the benchmark body fails. Benchmarks using this helper can keep their own state on the receiver.

## Risks and test signals

Risks include reflection method-set surprises for pointer versus value receivers, non-deterministic method ordering, and accidentally running helper methods prefixed with `Benchmark`. Signals are sub-benchmark execution and teardown counts covered by the companion test.
