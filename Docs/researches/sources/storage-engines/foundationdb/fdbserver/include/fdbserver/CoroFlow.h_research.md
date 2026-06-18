# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/CoroFlow.h

## Purpose
Provides interoperability helpers for using Flow futures from coroutine-style or blocking bridge code.

## Important APIs, Types, and Functions
- `CoroThreadPool::init()` initializes coroutine/thread-pool support.
- `CoroThreadPool::waitFor(Future<Void>)` waits for Flow future completion.
- `CoroThreadPool::createThreadPool()` creates an `IThreadPool`.
- `waitForAndGet(Future<T>)` waits on non-ready futures and returns the value.
- `waitFor(Future<Void>)` waits and throws the future error if present.

## Control Flow
Callers initialize once, then bridge Flow futures through the helper functions. `waitForAndGet` waits on `success(f)` before calling `f.get()`.

## State and Persistence Behavior
No persistent state; thread-pool state is hidden behind implementation elsewhere.

## Dependencies and Integration Points
Includes `fdbrpc/fdbrpc.h` and `flow/IThreadPool.h`. `fdbserver.cpp` calls `CoroThreadPool::init()` before role dispatch.

## Risks and Edge Cases
Blocking on Flow futures can deadlock if used on the wrong thread or before initialization. Error propagation relies on `get()` after waiting.

## Test Signals
No direct tests in this subset; exercised by server startup and coroutine interop paths.
