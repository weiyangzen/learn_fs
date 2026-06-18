# sources/user-network-fs/nfs-ganesha/src/include/fridgethr.h

## Purpose
`fridgethr.h` declares Ganesha's thread fridge, a POSIX-thread pool abstraction used for request decoding, async state work, idmapper reaping, FSAL upcalls, FD LRU cleanup, and other background loops.

## Important APIs, Types, And Functions
Core types are opaque `struct fridgethr`, `struct fridgethr_entry`, nested `struct fridgethr_context`, `struct fridgethr_params`, and `struct fridgethr_work`. `fridgethr_flavor_t` selects worker versus looper behavior. `fridgethr_defer_t` selects fail-fast versus queueing when full. Commands are run, pause, and stop. Public APIs initialize/destroy fridges, submit work, wake loopers, pause/stop/start asynchronously, run synchronous commands, ask a looper whether it should break, populate looper threads, adjust per-context wait, cancel threads, and initialize/shutdown the global `general_fridge`.

## Control Flow
`fridgethr_submit` dispatches to an idle thread, spawns if below `thr_max`, queues if allowed, or returns `EWOULDBLOCK`. Worker threads repeatedly run `ctx.func`, call optional cleanup, then freeze waiting for more work, timeout, pause, or stop. Looper fridges run a submitted function repeatedly with `thread_delay` sleeps and optional wake callbacks. Pause/start/stop set command state and notify completion through callback/condition variables; `fridgethr_sync_command` wraps those transitions with a timeout.

## State And Persistence
Fridge state is entirely in memory: thread lists, idle queues, queued work, command state, transition callback state, pthread attrs/locks, per-thread context, flags, and wait timeout. The global `op_ctx` TLS is declared in `fsal.h` but actually defined in `fridgethr.c`, so fridge threads are central to request-local context handling.

## Dependencies And Integration Points
It depends on project list and wait queue utilities, pthread wrappers from `common_utils.h` in implementation, RCU thread registration, logging, and `nfs_core.h`. Integration points include `state_async.c`, `idmapper.c`, `log_functions.c`, `FSAL_UP/fsal_up_async.c`, `FSAL/commonlib.c`, and FSAL-specific async fridges.

## Risks
Thread cancellation is asynchronous during hard teardown, so code running in fridge threads must be robust to process shutdown paths. Queueing fridges can accumulate unbounded work unless callers bound submissions. Transition state rejects overlapping pause/start/stop with `EBUSY`. Looper and worker parameters have strict compatibility rules, especially `wake_threads` only for loopers and no queue deferment for loopers.

## Test Signals
Tests should cover invalid parameters, submit with null/stopped/paused fridges, dispatch to idle threads, spawn up to `thr_max`, queued work drain, worker timeout exit above `thr_min`, pause/start/stop callbacks and sync timeouts, looper wake behavior, task cleanup, thread init/finalize hooks, and global fridge init/shutdown.
