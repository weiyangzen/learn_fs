# sources/storage-engines/foundationdb/flow/bench/BenchCoroChooseRace.cpp

Purpose: defines Google Benchmark microbenchmarks comparing Flow C++ coroutine `Choose()` selection against `race()` for two-result futures. It measures both side-effect-only selection and value-returning selection with `std::variant<int,double>`.

Important APIs/types/functions: internal enums `Impl` and `Scenario`; helpers `consumeReady`, `consumeAfter`, `selectReadyAsValue`, `selectAfterAsValue`; actor benchmarks `benchChooseRaceActor`, `benchChooseRaceValueActor`, and `benchChooseRaceConstructPendingActor`; wrappers run work through `onMainThread(...).blockUntilReady()`.

Control flow: each benchmark constructs ready, never-ready, or promise-completed futures and dispatches compile-time branches for `Choose` versus `race`. The pending-construction benchmark resumes timing only around selector construction and pauses before cancellation to isolate registration overhead.

State/persistence: no persistent state. Local `sink` variables prevent optimization. Promises and futures are per-iteration or per-actor local; pending futures are explicitly cancelled after timed construction.

Dependencies/integration: relies on `benchmark/benchmark.h`, Flow coroutine support from `flow/genericactors.actor.h`, and main-thread execution via `flow/ThreadHelper.actor.h`. Registered benchmark names group results under `coro_choose`, `coro_race`, and construct/value variants.

Risks: assertions assume synchronously ready futures after promise send or ready inputs; semantic changes in `Choose`, `race`, cancellation, or ready future propagation will break benchmark assumptions. The value-selection `Choose` path uses an extra `Promise<Result>`, intentionally measuring a different adaptation cost.

Test signals: the registered benchmark matrix covers ready-first, ready-second, after-first, value-returning, and pending construction cases, with `ReportAggregatesOnly(true)`.
