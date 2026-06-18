## sources/storage-engines/foundationdb/flow/bench/BenchAsyncResult.cpp

Purpose: this benchmark file measures C++20 coroutine performance for `Future<T>` versus `AsyncResult<T>` and aggregation helpers when moving/copying moderately expensive payloads through Flow async APIs.

Important types and APIs: `ExpensivePayload` owns a byte vector initialized with `std::iota` and a `touch()` method that reads first/middle/last bytes. `returnFuturePayload` and `returnAsyncResultPayload` are coroutine producers. Benchmark template families cover single await (`benchAwaitPayloadActor`/`benchAwaitPayload`), `getAll`/`getAllAsync` over `Future<ExpensivePayload>` inputs, and `getAll`/`getAllAsync` over freshly produced `AsyncResult<ExpensivePayload>` inputs. Enum template parameters select implementation variants.

Control flow: each benchmark runs a Flow coroutine on the main thread via `onMainThread(...).blockUntilReady()`. Inside `benchmark::State` loops, it awaits or aggregates payload futures/results, touches payloads to prevent dead-code elimination, calls `ClobberMemory`, and records processed bytes.

State and persistence behavior: state is benchmark-local. Payload sources are reused where appropriate; some variants allocate vectors of async results inside each iteration to include production/aggregation cost. No persistent storage is touched.

Dependencies and integration points: depends on Google Benchmark, Flow coroutine/future APIs from `flow/flow.h`, `flow/genericactors.actor.h`, and `flow/ThreadHelper.actor.h`. It benchmarks runtime coroutine paths rather than actor compiler output.

Risks: benchmark numbers depend on payload copy elision/move behavior, vector allocation, main-thread scheduling overhead, and whether inputs are already ready. The `AsyncResult` aggregate benchmark constructs inputs inside the timing loop, so it measures more than aggregation alone. `ASSERT(!bytes.empty())` assumes benchmark ranges are nonzero.

Test signals: build success with coroutine-enabled Flow, benchmark registration names, nonzero bytes processed, and stable relative results across payload sizes. It can also catch regressions in `getAll`/`getAllAsync` support for `AsyncResult`.
