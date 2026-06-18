## sources/storage-engines/foundationdb/flow/bench/BenchCallbackActor.cpp

Purpose: this benchmark file measures the same callback fan-out/fan-in shape as `BenchCallback.cpp`, using Flow coroutine functions named in the actor benchmark style.

Important APIs: `increment<Size>(Future<Void>, uint32_t*)` allocates a `std::array<uint8_t, Size>`, awaits a trigger future, prevents optimization, and increments a shared sum. `benchCallbackActor<Size>` creates `actorCount` increments, sends the trigger, awaits `waitForAll`, and records item/byte throughput. `bench_callback<Size>` runs it on the main thread. Benchmark registrations cover sizes 1, 32, and 1024 over range 1 to 256.

Control flow: per iteration, reset `sum`, create one promise and many futures, fire the promise, wait for all callbacks to resume, and update benchmark counters after the loop.

State and persistence behavior: all state is local to the benchmark and coroutine frames. No persistent storage.

Dependencies and integration points: depends on Google Benchmark, `flow/flow.h`, and `flow/ThreadHelper.actor.h`. It is a performance integration point for Flow future/coroutine scheduling and callback fan-out.

Risks: the function returns `Future<Void>` but falls off the end without an explicit `co_return`; this may compile due to coroutine promise behavior but is a portability/readability risk compared with the explicit `co_return` in `BenchCallback.cpp`. As with the coroutine variant, shared `sum` assumes single-threaded cooperative execution. `std::array` requires the included headers to supply `<array>` transitively or elsewhere.

Test signals: successful compilation, benchmark registration, processed counters, and comparison against `BenchCallback.cpp` and historical actor callback benchmarks.
