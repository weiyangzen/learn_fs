# sources/storage-engines/foundationdb/flow/IThreadPool.cpp

## Purpose
Implements the generic Flow `IThreadPool` using Boost ASIO for cross-thread action dispatch and Flow thread startup/stop semantics.

## Important APIs, Types, And Functions
`ThreadPool` implements `IThreadPool`. Nested `Thread` owns an `IThreadPoolReceiver`, worker handle, TLS receiver pointer, `run()`, and `dispatch()`. `ActionWrapper` owns/cancels `PThreadAction`. Public methods include `stop()`, `getError()`, `addref()`, `delref()`, `addThread()`, `post()`, and `priority()`. `createGenericThreadPool()` constructs the reference-counted pool.

## Control Flow
Each added thread starts via `g_network->startThread()`, sets priority and TLS receiver, calls receiver `init()`, then runs one ASIO handler at a time while mode is `Run`. Posting wraps the action; wrapper copy semantics transfer ownership because Boost may copy handlers. Stop sets shutdown, stops ASIO, waits all thread handles, deletes thread records, and carefully adjusts refcounts to handle explicit and implicit destruction paths.

## State And Persistence Behavior
State is in-process: worker vector, ASIO service/work guard, shutdown mode, stack size, priority, and thread-local receiver pointer. No persistence.

## Dependencies And Integration Points
Depends on `IThreadPool.h`, Boost ASIO, Flow network thread creation, priorities, TraceEvent, `Error`, `ReferenceCounted`, `ThreadAction`, and `IThreadPoolReceiver` implementations.

## Risks And Edge Cases
`getError()` returns `Never()` and is marked FIXME, so worker failures only trace. `ios.stop()` comment says it may not work as expected, making mode and joins important. Handler ownership relies on a custom copy hack. Receiver deletion happens on worker exit; callers must not retain raw receiver ownership after `addThread()`.

## Test Signals
Covered by `IThreadPoolTest.cpp` for named threads, promise streams, explicit stop, and implicit destruction.
