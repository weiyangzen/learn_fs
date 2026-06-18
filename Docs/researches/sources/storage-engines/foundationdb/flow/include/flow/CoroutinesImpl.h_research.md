# sources/storage-engines/foundationdb/flow/include/flow/CoroutinesImpl.h

## Purpose
`CoroutinesImpl.h` implements Flow's C++ coroutine runtime: promise types, awaiters for `Future`, `FutureStream`, `ThreadFutureStream`, and `AsyncResult`, actor-backed return objects, cancellation semantics, and generator promises.

## Important APIs, Types, And Functions
Important internals include `AwaitCancelHandler`, `FutureReturnType`, `GetFutureType`, `CoroActor`, `NoThrowOnCancelCoroActor`, `AsyncResultCallback`, `AsyncResultState`, `AwaitableFutureStore`, `AwaitableAsyncResult`, `AwaitableFuture`, `AwaitableFutureOwning`, `AwaitableFutureIgnore`, `AwaitableFutureErrorOr`, `ThreadAwaitableFutureStream`, `CoroPromise`, `AsyncResultPromise`, `GeneratorPromise`, `AsyncGeneratorPromise`, and marker detectors such as `hasUncancellable`.

## Control Flow
Promises start immediately with `suspend_never`. Await transforms register callbacks, set actor wait state, and resume the coroutine from callback `fire()`/`error()`. Normal cancellation marks the actor cancelled and resumes so `await_resume()` throws `actor_cancelled()`. `NoThrowOnCancel` unregisters the active wait source and destroys the coroutine frame. Final suspend writes the result/error into `SAV` or `AsyncResultState` and wakes consumers.

## State And Persistence Behavior
State lives in coroutine frames, embedded or separately allocated actor state, `AsyncResultState` reference counts, aligned value storage, callback/continuation pointers, producer handles, wait-state bytes, and optional stream value stores. Fast allocation is used for coroutine frames and async result states. `AsyncResultState::complete()` clears producer handles before firing callbacks or continuations.

## Dependencies And Integration Points
This file depends on `FlowThread.h`, `flow.h`, Flow actor wait-state constants, `SAV`, callback classes, `Future`, `StrictFuture`, `FutureStream`, `ThreadFutureStream`, `PromiseStream`, `Error`, `Void`, `allocateFast`, and `freeFast`.

## Risks And Edge Cases
Lifetime is delicate: callbacks and cancel handlers often live in coroutine frames, so no-throw cancellation must detach them before frame destruction. `AsyncResultState` supports one callback or one continuation. Stream awaiters need local storage because values may arrive through callbacks rather than remaining in stream queues. Final suspend hot-path changes can break `SAV` ownership.

## Test Signals
Stress tests should cover cancellation during ready check, while suspended, and after completion; no-throw cancellation; nested `AsyncResult`; `ignore()` and `errorOr()` adapters; stream errors and values; `ThreadFutureStream`; unknown exceptions converting to `unknown_error`; and ASAN/TSAN checks for callback-after-free.
