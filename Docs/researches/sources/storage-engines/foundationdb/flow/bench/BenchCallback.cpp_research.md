## sources/storage-engines/foundationdb/flow/bench/BenchCallback.cpp

Purpose: this benchmark file measures callback fan-out/fan-in overhead using C++20 coroutine-style Flow code. The comment positions it as a coroutine version of callback benchmarks matching a `BenchNet2.cpp` pattern.

Important APIs: `incrementCoro<Size>(Future<Void>, uint32_t*)` allocates a stack buffer of `Size`, waits on a trigger future, prevents optimization of the buffer, and increments a shared sum. `benchCallbackCoro<Size>` creates many increment coroutines waiting on one promise, sends the trigger, waits for all futures, and records processed items/bytes. `coroutine_callback<Size>` runs the benchmark actor on the main thread.

Control flow: for each benchmark iteration, create `actorCount` futures, trigger them all with one `Promise<Void>`, await `waitForAll`, and account for work. Template registrations cover stack sizes 1, 32, and 1024 with actor counts from 1 to 256.

State and persistence behavior: benchmark state is local: `sum`, `Promise`, and vector of futures per iteration. No persistence.

Dependencies and integration points: depends on Google Benchmark and Flow headers (`IRandom`, `flow`, `DeterministicRandom`, `network`, `ThreadHelper.actor.h`), though random/network includes are not directly used in the visible code. It integrates with Flow's main-thread execution helper.

Risks: `uint8_t arr[Size]` is uninitialized but only passed to `DoNotOptimize`; this is acceptable for benchmarking stack footprint but compiler behavior should be watched. The shared `sum` pointer assumes all continuations run cooperatively on the Flow main thread, avoiding data races. Include drift can add unnecessary compile dependencies.

Test signals: benchmark compile/register/run, items and bytes processed matching actor count and size, and comparison against actor-style callback benchmarks.
