# sources/storage-engines/foundationdb/flow/include/flow/Coroutines.h

## Purpose
`Coroutines.h` is the public Flow coroutine facade. It selects `<coroutine>` or `<experimental/coroutine>`, defines marker parameters, exposes `AsyncResult<T>`, includes the promise/awaiter implementation, and defines `AsyncGenerator<T>` and synchronous `Generator<T>`.

## Important APIs, Types, And Functions
Key public types are `Uncancellable`, `NoThrowOnCancel`, `ExplicitVoid`, `coro::ignore()`, `coro::errorOr()`, `AsyncResult<T>`, `AsyncGenerator<T>`, and `Generator<T>`. `AsyncResult` exposes move-only ownership, readiness/error inspection, `get()`, cancellation, callback registration, and `operator co_await()`.

## Control Flow
Coroutine return types are wired by promise types in `CoroutinesImpl.h`. `AsyncResult` wraps a shared state produced by an `AsyncResultPromise`; awaiting it either resumes immediately or registers a continuation/callback. `AsyncGenerator::operator()()` resumes the generator, waits on an internal `PromiseStream`, delays one tick, then returns the yielded value or rethrows a stored Flow error.

## State And Persistence Behavior
`AsyncResult` owns a pointer to `AsyncResultState` and transfers ownership by move; destruction releases a reference and can cancel producers. `AsyncGenerator` stores a `PromiseStream<T>*` and coroutine handle and destroys the handle on destruction. `Generator` reference-counts its promise so copies share one coroutine frame.

## Dependencies And Integration Points
It integrates C++ coroutines with Flow `Future`, `FutureStream`, `PromiseStream`, `Void`, `Error`, actor cancellation, Swift sendability/reference annotations, and the implementation in `flow/CoroutinesImpl.h`.

## Risks And Edge Cases
`AsyncResult` is intentionally move-only; copying would duplicate value ownership. `ExplicitVoid` changes `co_await Future<Void>` resume type. `NoThrowOnCancel` bypasses coroutine catch blocks on cancellation. `AsyncGenerator` assumes its promise stream outlives calls through the coroutine frame and destroys the handle unconditionally.

## Test Signals
Compile coroutine call sites for normal, uncancellable, no-throw-cancel, and explicit-void signatures; test `AsyncResult` move/get/cancel/error paths; test generator copy/destruction reference behavior; and run under sanitizers for coroutine-frame lifetime.
