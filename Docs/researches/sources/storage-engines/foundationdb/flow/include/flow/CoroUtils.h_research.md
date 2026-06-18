# sources/storage-engines/foundationdb/flow/include/flow/CoroUtils.h

## Purpose
`CoroUtils.h` adds higher-level coroutine utilities on top of Flow futures: `Choose`, `race()`, async-generator filtering, and conversion from `FutureStream<T>` to `AsyncGenerator<T>`. It lets coroutine code express actor-style wait choices without the actor compiler.

## Important APIs, Types, And Functions
Important pieces are `coro::ActorAsyncResultCallback`, `ConditionalActorCallback`, `ChooseImplCallback`, `ChooseImplActor`, `ChooseClause::When()`, `ChooseClause::run()`, `coro::RaceResult`, `raceReadyResult()`, `raceReady()`, `RaceImplCallback`, `RaceImplActor`, public alias `Choose`, free function `race()`, `map()`, and `toGenerator()`.

## Control Flow
`ChooseClause` accumulates futures/streams plus void handlers. If a clause is already ready, it runs immediately and later clauses become no-ops; otherwise `run()` creates a `ChooseImplActor` that registers one callback per input and completes after the first callback fires or errors. `race()` first checks already-ready inputs in argument order, then creates `RaceImplActor`, which removes all callbacks and returns a variant indexed by the winning input.

## State And Persistence Behavior
State is transient actor state: tuples of awaitables, callbacks, handlers, wait-state flags, and `SAV` completion storage. Stream winners consume one queued item. Non-winning inputs are detached, not directly cancelled. `map()` and `toGenerator()` preserve generator/stream progress until end-of-stream or error.

## Dependencies And Integration Points
It depends on `flow/flow.h`, coroutine traits from `CoroutinesImpl.h`, Flow callback types (`ActorCallback`, `ActorSingleCallback`), `Future`, `FutureStream`, `AsyncResult`, `Actor`, `FastAllocated`, `LineageScope` under sampling, and Flow errors.

## Risks And Edge Cases
Callback removal order is critical because callbacks point into actor objects. Ready checks favor the lowest index. `FutureStream` clauses pop exactly one item. `Choose` handlers must be synchronous void functions. `AsyncResult` must be moved into callback registration for race. Non-winning operations can still run if other references keep them alive.

## Test Signals
Useful tests cover ready and delayed futures, streams, `AsyncResult`, errors, cancellation, callback removal, lowest-index tie behavior, handler exceptions, stream consumption count, `toGenerator()` end-of-stream handling, and lineage sampling builds.
