# sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlowCoro.actor.cpp

## Purpose
This file is the older libcoroutine-based `CoroThreadPool` implementation, used on Windows until Boost.Context is available in CI.

## Important APIs, Types, And Functions
Global `current_coro`, `main_coro`, and `swapCoro` manage coroutine switching. `Coroutine` wraps raw `Coro*`, with `start`, `unblock`, `block`, `wrapRun`, and static `entry`. The same `WorkPool<Threadlike, Mutex, IS_CORO>` pattern implements `IThreadPool`. `coroSwitcher` waits on a Flow future then switches back to a coroutine. `CoroThreadPool::waitFor`, `init`, and `createThreadPool` expose the API.

## Control Flow
`init` creates and initializes the main coroutine. Worker coroutines run the same queue loop as the Boost implementation: initialize user data, execute queued actions, yield, block when idle, and stop on errors or explicit shutdown. `waitFor` schedules `coroSwitcher`, switches to `main_coro`, and resumes once the future is ready.

## State And Persistence Behavior
All state is process-local coroutine scheduler state and work-pool queues. There is no durable state.

## Dependencies And Integration Points
It depends on `Coro.h`, Flow actors, simulator info, tracing, and `CoroFlow.h`. It is a platform-specific implementation behind the same `IThreadPool` contract as the Boost version.

## Risks And Edge Cases
Manual coroutine switching is fragile: `current_coro`/`main_coro` must be initialized, `waitFor` cannot run on the main coroutine, and future errors are only asserted ready here rather than explicitly rethrown. Allocation failure maps to `platform::outOfMemory`.

## Test Signals
Tests should match the Boost implementation: action execution, idle unblocking, stop cleanup, error propagation, future wait/resume behavior, Windows build coverage, and no hangs during simulated reboot timing.
