# sources/storage-engines/foundationdb/flow/include/flow/IThreadPool.h

## Purpose
`IThreadPool.h` defines Flow's abstraction for blocking disk-intensive worker pools and typed actions that return results to the network thread.

## Important APIs, Types, And Functions
Important types are `IThreadPoolReceiver`, `ThreadAction`, `IThreadPool`, `TypedAction<Object,ActionType>`, `ThreadReturnPromise<T>`, `createGenericThreadPool()`, and `DummyThreadPool`.

## Control Flow
Clients add receiver instances with `addThread()`, then post self-deleting actions. `TypedAction` casts the receiver and action to concrete types, runs `receiver->action()`, and deletes the action. `ThreadReturnPromise` forwards success or error to the main thread through `g_network->onMainThread()`.

## State And Persistence Behavior
Thread pools own implementation-specific workers. `ThreadReturnPromise` owns a Flow promise until sent, errored, or destroyed, where it sends `broken_promise()`. `DummyThreadPool` runs work synchronously against one receiver and stores internal errors in a promise.

## Dependencies And Integration Points
It depends on `flow.h`, `FlowThread.h`, `Reference`, `g_network`, task priorities, and thread return tagging helpers. It integrates with async file backends and blocking I/O offload.

## Risks And Edge Cases
`ThreadAction::operator()` self-destructs by convention; violating this leaks or double-frees. `ThreadReturnPromise::getFuture()` must be called on the originating thread before send. Result delivery priority depends on whether send happens on main thread.

## Test Signals
Tests should cover action execution/cancel deletion, worker init, stop/error futures, cross-thread result/error delivery, broken promise on destruction, dummy pool synchronous behavior, and simulation time estimates.
