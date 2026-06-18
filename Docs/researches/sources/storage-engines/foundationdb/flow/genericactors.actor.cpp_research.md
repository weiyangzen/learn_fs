# sources/storage-engines/foundationdb/flow/genericactors.actor.cpp

Purpose: implements generic Flow actor/coroutine utilities and unit tests for async listeners, quorum helpers, wait-most behavior, and coroutine equivalents in `genericcoros.h`.

Important APIs/types/functions: `allTrue`, actor `anyTrue`, `cancelOnly`, `timeoutWarningCollector`, `waitForMost`, `quorumEqualsTrue`, `shortCircuitAny`, `orYield`, `returnIfTrue`, `lowPriorityDelay`, `delayAfterCleared`, `lowPriorityDelayAfterCleared`, plus test helpers.

Control flow: utilities compose futures with ACTOR `choose`, `wait`, `waitForAny`, `quorum`, and coroutine awaits. `waitForMost` maps `ErrorOr<Void>` futures to success booleans, waits for quorum, optionally waits longer for slow futures, and throws configured error on insufficient success.

State/persistence: actor state variables track counters, timers, vectors, and previous async-var values. No disk persistence.

Dependencies/integration: includes Flow core, unit tests, `genericcoros.h`, and actor compiler last. It exposes general helpers used throughout FoundationDB actor code.

Risks: actor/coroutine interop and cancellation behavior are subtle. `lowPriorityDelay` loop count depends on knobs. `shortCircuitAny` handles a race between final completion and short-circuit path.

Test signals: unit tests cover `IAsyncListener`, `waitForMost`, and generic coroutine helpers for error transformation, tracing, timeout, delayed propagation, trigger, and wait-for-all-ready.
