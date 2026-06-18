# sources/storage-engines/foundationdb/flow/bench/BenchTimer.cpp

Purpose: benchmarks Flow platform time accessors.

Important APIs/types/functions: `bench_timer` calls `timer()` and `bench_timer_monotonic` calls `timer_monotonic()`.

Control flow: each benchmark repeatedly invokes the selected clock function and prevents optimization of the result.

State/persistence: no local or persistent state.

Dependencies/integration: includes `flow/Platform.h` and Google Benchmark. These functions are low-level timing sources used broadly in Flow and simulation code.

Risks: results are platform-dependent and sensitive to clock implementation, syscall/vDSO behavior, and CPU frequency settings.

Test signals: two aggregate benchmark registrations set item count to iterations.
