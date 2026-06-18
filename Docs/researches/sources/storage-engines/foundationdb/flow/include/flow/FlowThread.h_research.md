# sources/storage-engines/foundationdb/flow/include/flow/FlowThread.h

## Purpose
`FlowThread.h` implements thread-to-main-thread future stream plumbing, allowing worker threads to send values or errors back to the Flow network thread.

## Important APIs, Types, And Functions
Important templates are `ThreadNotifiedQueue<T>`, `ThreadFutureStream<T>`, `ThreadReturnPromiseStream<T>`, and declaration `waitNext()`. Core methods include `send()`, `sendError()`, `addCallbackAndDelFutureRef()`, `pop()`, `getFuture()`, and reference-count helpers.

## Control Flow
Worker-side `send()` posts a lambda to the main thread; the lambda either fires a waiting callback or enqueues the value. `sendError()` records an error and fires a callback only when queued values are drained. Futures add/drop queue references; dropping the last future cancels producers, and dropping the last promise sends `broken_promise()` if futures remain.

## State And Persistence Behavior
`ThreadNotifiedQueue` stores promise/future reference counts, an error, a `std::queue<T, Deque<T>>`, a spin lock, and callback list sentinel state. State persists until both sides release their references.

## Dependencies And Integration Points
It depends on `flow.h`, `FastAlloc`, `ThreadPrimitives`, `ThreadHelper.actor.h`, `ScopeExit`, and `Buggify`. `CoroutinesImpl.h` provides awaiters for `ThreadFutureStream`.

## Risks And Edge Cases
The header notes futures should currently be used only from the main thread. Error visibility waits for queued values to drain. `send()` captures values into a main-thread lambda, so value copy/move semantics matter. Reference-count transitions can trigger cancellation or destruction while callbacks are involved.

## Test Signals
Tests should cover cross-thread sends, callback vs queued delivery, error after values, broken promise, future drop cancellation, multiple future references, `ThreadFutureStream` await, and TSAN/lock-order checks.
