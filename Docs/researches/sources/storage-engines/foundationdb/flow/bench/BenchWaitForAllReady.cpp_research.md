# sources/storage-engines/foundationdb/flow/bench/BenchWaitForAllReady.cpp

Purpose: compares actor and coroutine implementations of `waitForAllReady` over already-completed futures, including success and error futures.

Important APIs/types/functions: enums `WaitForAllReadyImpl` and `WaitForAllReadyScenario`; `makeResults`; `benchWaitForAllReadyActor`; wrapper `benchWaitForAllReady`.

Control flow: prebuilds a vector of ready `Future<int>` objects or futures already set to `operation_failed()`, then repeatedly invokes actor `::waitForAllReady` or `generic_coro::waitForAllReady` and awaits completion.

State/persistence: immutable vector of futures for a benchmark state. No durable state.

Dependencies/integration: uses Flow generic actor helpers, `genericcoros.h`, main-thread execution, and Google Benchmark.

Risks: only covers all-ready inputs, so it isolates iteration and error-suppression overhead, not asynchronous fan-in latency. Error scenario assumes the implementation waits for readiness without propagating errors.

Test signals: four registered benchmark series cover actor/coroutine and ready/error cases with ranges 1 to 4096 futures.
