# sources/storage-engines/foundationdb/flow/include/flow/genericactors.actor.h

## Purpose
Reusable Flow actor utilities for transforming futures, timeouts, streams, async variables, wait aggregation, locks, recurring tasks, weak future references, and simulation-friendly singletons.

## Important APIs, Types, And Functions
Key APIs include `traceAfter`, `stopAfter`, `errorOr`, `throwErrorOr`, `transformErrors`, `timeout`, `timeoutError`, `delayed`, `uncancellable`, `map`, `mapAsync`, `waitForAll`, `waitForAny`, `getAll`, `appendAll`, `waitForFirst`, `tag`, `orYield`, `recurring`, `recurringAsync`, `brokenPromiseToNever`, `AsyncMap`, `YieldedAsyncMap`, `AsyncVar`, `AsyncTrigger`, `Debouncer`, `FlowMutex`, `FlowLock`, `BoundedFlowLock`, `IAsyncListener`, `UnsafeWeakFutureReference`, and `FlowSingleton`.

## Control Flow
Actor and coroutine helpers compose futures with `wait`, `choose`, callbacks, and promises. Quorum/getAll attach callbacks and complete on success thresholds or first error. `AsyncVar` swaps next-change promises before setting. `FlowLock` queues waiters and yields after acquisition to avoid release-stack reentrancy.

## State And Persistence Behavior
State is process-local coordination state: wait queues, promises, maps, locks, debounce workers, and simulated-address singleton maps. It coordinates persistent subsystems but persists nothing itself.

## Dependencies And Integration Points
Depends on `flow.h`, task priorities, knobs, indexed sets, utility helpers, and actor compiler macros. Included broadly by Flow and server/client actor code.

## Risks And Edge Cases
Cancellation and ownership are subtle, especially with single-consumer `AsyncResult` vectors. `FlowLock` is not thread-safe. `AsyncMap` cleanup relies on promise reference counts. `UnsafeWeakFutureReference` can dangle if object lifetime is not externally controlled.

## Test Signals
Generic actor/coroutine tests for AsyncListener, WaitForMost, trace/timeout/delayed/trigger/error transforms, Flow quorum tests, and storage-engine `FlowLock` throttling tests.
