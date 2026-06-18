# sources/storage-engines/foundationdb/flow/bench/BenchRandom.cpp

Purpose: measures throughput of Flow's thread-local deterministic RNG `random01()`.

Important APIs/types/functions: `bench_random` and `deterministicRandom()->random01()`.

Control flow: each iteration calls `random01()` and uses `benchmark::DoNotOptimize` to retain the call.

State/persistence: relies on Flow's thread-local deterministic RNG state initialized elsewhere. The benchmark itself has no stored state.

Dependencies/integration: includes `flow/IRandom.h` and Google Benchmark. It exercises the global RNG accessor defined in `flow.cpp`.

Risks: benchmark timing includes accessor cost as well as random generation. Because RNG state is global/thread-local, prior tests can influence sequence position but not the cost model materially.

Test signals: one aggregate benchmark with item count set to iteration count.
