# sources/storage-engines/foundationdb/flow/bench/BenchTimeout.cpp

Purpose: compares actor-based `timeout` from `genericactors.actor.h` with coroutine-based `generic_coro::timeout`.

Important APIs/types/functions: enums `TimeoutImpl` and `TimeoutScenario`; template actor `benchTimeoutActor`; wrapper `benchTimeout`; overloads returning a timed-out value.

Control flow: ready scenario repeatedly wraps a ready future with zero timeout and awaits the result. construct-pending scenario measures construction of a timeout race on a never-ready future with a one-second timer, pauses timing, and cancels the pending result.

State/persistence: local sink for ready values and local never/ready futures. No durable state.

Dependencies/integration: Flow generic actor helpers, `genericcoros.h`, main-thread execution, and Google Benchmark.

Risks: ready scenario includes await cost after wrapper construction; pending scenario explicitly excludes cancellation cleanup. Semantics depend on timeout implementation preserving ready fast paths and cancellation behavior.

Test signals: four benchmarks cover actor/coroutine implementations in ready and pending construction modes.
