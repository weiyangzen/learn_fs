# sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlow.actor.cpp

## Purpose
This file implements `CoroThreadPool` using Boost.Coroutine2 so blocking-style thread-pool receivers can interoperate with Flow futures without native OS threads.

## Important APIs, Types, And Functions
`Coroutine` wraps a Boost `pull_type`/`push_type` pair, fixed 256 KiB stack, `start`, `unblock`, `waitFor`, `switcher`, `entry`, and `block`. `WorkPool<Threadlike, Mutex, IS_CORO>` implements `IThreadPool` with nested `Pool` and `Worker`. Public methods are `getError`, `addThread`, `post`, `stop`, `isCoro`, `addref`, and `delref`. `CoroThreadPool::waitFor`, `init`, and `createThreadPool` complete the integration.

## Control Flow
`addThread` creates a worker coroutine and starts it after a zero-delay yield so Net2 is running. Workers initialize user data, take queued `PThreadAction`s, execute them, yield between actions, and block when idle. `post` queues work and unblocks one idle coroutine. `stop` cancels queued actions, marks workers stopped, unblocks idle workers, and returns the all-stopped future.

## State And Persistence Behavior
State is process-local: current coroutine pointer, work queue, idle/worker lists, actor collections for errors/stops, and user data. There is no persistence.

## Dependencies And Integration Points
It depends on `CoroFlow.h`, `ActorCollection`, metrics/tracing, simulator process info, Boost.Coroutine2, Flow network, and actorcompiler. It provides an `IThreadPool` implementation for components expecting a thread-pool API.

## Risks And Edge Cases
Coroutine lifetime is guarded by a shared `alive` flag because the switcher actor can outlive `Coroutine`. Error propagation stops the pool. `CoroThreadPool::waitFor` asserts it runs inside a coroutine and rethrows future errors after resumption. Stack size and action cancellation callbacks are sensitive.

## Test Signals
Signals include posted actions executing in order, idle wakeups, error propagation stopping the pool, clean deletion of user data, stop completion, future-error rethrowing, and simulation reboot traces not hanging.
