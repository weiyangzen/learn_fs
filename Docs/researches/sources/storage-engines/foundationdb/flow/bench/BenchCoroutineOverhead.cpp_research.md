# sources/storage-engines/foundationdb/flow/bench/BenchCoroutineOverhead.cpp

Purpose: measures baseline overhead of Flow C++ coroutine futures for immediate `co_return` and immediate `co_await` on ready values.

Important APIs/types/functions: `returnReadyInt`, `returnReadyVoid`, `benchCreateReadyIntActor`, `benchCreateReadyVoidActor`, `benchAwaitReadyIntActor`, `benchAwaitReadyVoidActor`, and non-actor benchmark wrappers that execute on the Flow main thread.

Control flow: create benchmarks repeatedly call a coroutine that returns an already-ready `Future<T>`, assert readiness, consume the result where applicable, and use `DoNotOptimize`. Await benchmarks keep a prebuilt ready `Future<int>` or `Future<Void>` and repeatedly `co_await` it inside the benchmark actor.

State/persistence: only local counters and ready futures. There is no durable state or heap ownership beyond normal future frames.

Dependencies/integration: depends on Google Benchmark, `flow/flow.h`, and `ThreadHelper.actor.h`. Benchmark registration names use `coroutine_overhead/...`, providing a focused signal for Flow coroutine implementation changes.

Risks: because all inputs are ready, results are sensitive to compiler optimization, coroutine ABI behavior, and future fast-path changes. Assertions hard-code that these coroutines complete synchronously.

Test signals: benchmark registrations cover ready int/void creation and ready int/void await; `SetItemsProcessed` is not used, so timing is per benchmark iteration only.
