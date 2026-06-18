# sources/user-network-fs/nfs-ganesha/src/support/fridgethr.c

## Purpose
`fridgethr.c` implements Ganesha's "thread fridge": a POSIX-thread based worker/looper pool that can submit jobs, queue or reject overflow, pause, stop, restart, wake loopers, synchronously wait for transitions, and cancel workers during shutdown. It also defines the thread-local `op_ctx` pointer used by NFS operation and support threads.

## Important APIs, Types, And Functions
The companion header defines `struct fridgethr`, `struct fridgethr_entry`, `struct fridgethr_context`, `struct fridgethr_params`, `struct fridgethr_work`, `fridgethr_flavor_t`, `fridgethr_defer_t`, and `fridgethr_comm_t`.

Primary APIs:

- `fridgethr_init()` validates min/max/flavor/deferment/wake settings, initializes detached pthread attributes, locks, lists, command state, and name.
- `fridgethr_destroy()` waits for `frt_mtx` availability, destroys lock/attrs, and frees the fridge object.
- `fridgethr_submit()` dispatches to an idle worker, spawns a new detached worker, queues work, or returns `EWOULDBLOCK`/`EPIPE`.
- `fridgethr_wake()` signals all idle threads.
- `fridgethr_pause()`, `fridgethr_stop()`, and `fridgethr_start()` change command state and arrange completion callbacks.
- `fridgethr_sync_command()` wraps the transition APIs with a private mutex/condition and optional timeout.
- `fridgethr_populate()` starts a fixed number of identical workers for a pre-populated pool.
- `fridgethr_setwait()` and `fridgethr_getwait()` mutate/read runtime wait delay.
- `fridgethr_cancel()` force-cancels all recorded threads during shutdown.
- `general_fridge_init()` and `general_fridge_shutdown()` create and stop the global general-purpose fridge.

Internal functions:

- `fridgethr_start_routine()` is the worker entry point: registers RCU, names the thread, enables cancellation, calls optional initialize/finalize hooks, executes jobs in a loop, runs task cleanup, and freezes or exits.
- `fridgethr_freeze()` is the main state machine for waiting, queue draining, pause completion, timeout shrinkage, and stop exit.
- `fridgethr_dispatch()`, `fridgethr_spawn()`, `fridgethr_queue()`, `fridgethr_getwork()`, and `fridgethr_deferredwork()` implement scheduling mechanics.
- `fridgethr_finish_transition()` invokes transition callbacks and broadcasts completion.

## Control Flow
A submitted worker job enters `fridgethr_submit()`. If the fridge is stopped it fails. If paused or full it follows the configured deferment policy. Otherwise it prefers an idle thread by setting that thread context, marking `fridgethr_flag_dispatched`, and signaling its condition variable. If no idle thread exists and capacity remains, it spawns a detached pthread running `fridgethr_start_routine()`.

Each worker runs `ctx.func(ctx)`, optional `task_cleanup(ctx)`, and then `fridgethr_freeze()`. In worker flavor, freeze first drains queued work unless paused. Otherwise the thread joins `idle_q`, waits on its per-thread condition variable or timed wait, and returns either with dispatched work, queued work, or an instruction to exit. Timed-out idle workers above `thr_min` shrink the pool. Stop transitions decrement `nthreads` and the last exiting thread completes the transition.

Pause sets `command = fridgethr_comm_pause`, marks `transitioning`, stores callback state, and completes immediately if every thread is already idle. Stop wakes idle threads and, if no thread exists but queued work exists, starts one worker to drain cleanup paths. Start switches back to run, wakes idle threads, and may spawn up to a bounded number of workers for deferred jobs.

`fridgethr_sync_command()` issues one of the state transitions and waits until `fridgethr_trivial_syncer()` flips a stack-local `done` flag or until timeout.

## State And Persistence Behavior
All state is process-local. `frt_mtx` protects fridge command state, transition state, thread counts, idle and work queues, callback fields, and delay settings. Each worker also has `fre_mtx` and `fre_cv` for dispatch handoff. Threads are created detached. `thread_info` and `uflags` are deliberately left for caller use.

`op_ctx` is `__thread`, so each fridge worker has its own operation context pointer. Worker startup registers with userspace RCU (`rcu_register_thread()`), and exit unregisters. The global `general_fridge` is a queueing worker fridge with max 32 and no minimum.

## Dependencies And Integration Points
The module depends on pthreads, signals, userspace RCU, Ganesha memory helpers, glists, logging, and `nfs_core.h`. It is used by asynchronous support work such as delegation transitions and recall paths in export management, plus other server worker pools that need pause/stop semantics.

Callers integrate by providing functions of type `void (*)(struct fridgethr_context *)`, optional thread/task hooks, optional looper wake callbacks, and shutdown coordination through sync commands or direct pause/start/stop.

## Risks And Edge Cases
`fridgethr_populate()` adds `fe->thread_link` to `thread_list` without the visible `glist_init()` used by `fridgethr_spawn()`. On `pthread_create()` failure it also returns after destroying sync primitives without removing the list entry, decrementing `nthreads`, or freeing `fe`. This path should be reviewed.

`fridgethr_sync_command()` returns early on transition API errors without destroying its private mutex and condition variable, producing a small resource leak on invalid, busy, or already-in-state calls.

Threads are configured detached, but `fridgethr_cancel()` calls `pthread_join()` after `pthread_cancel()`. Joining detached threads is invalid on POSIX and the code ignores the return. Since this is shutdown-only, the risk is mostly noisy/undefined cleanup rather than normal operation, but it deserves scrutiny.

`fridgethr_start()` lacks the explicit mutex/condition pair validation present in pause/stop. Passing only one of `pmtx` or `cv` can create odd completion semantics.

Asynchronous cancellation is enabled in worker threads. This is intentional for forced shutdown, but it means cancellation can interrupt code while locks or external resources are held.

## Test Signals
Useful tests include submit-to-idle, spawn-up-to-max, queue-on-full, fail-on-full, timed shrink above `thr_min`, pause while jobs run, stop with idle threads, stop while queued and no threads exist, start after pause with queued work, looper wake behavior, sync timeout behavior, populate failure injection, and shutdown cancellation. Thread sanitizer or stress tests around dispatch/freezing are valuable because correctness depends on per-thread flags and two mutex layers.
