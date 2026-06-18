# sources/storage-engines/wiredtiger/src/support/thread_group.c Research

## Purpose
This file implements WiredTiger's generic utility-thread group abstraction. A `WT_THREAD_GROUP` owns an array of `WT_THREAD` slots, a group rwlock, a condition used by waiters, and callback pointers supplied by the subsystem. The implementation separates thread existence from active work: resize creates or destroys thread/session/condition resources, while start and stop only toggle `WT_THREAD_ACTIVE` within the already allocated group.

## Important APIs, Types, and Functions
- `WT_THREAD_GROUP` stores `min`, `max`, `alloc`, `current_threads`, `threads`, `lock`, `wait_cond`, name, and callback pointers.
- `WT_THREAD` stores an internal session, thread id/name index, pause condition, run/check/stop callbacks, and flags such as `WT_THREAD_RUN`, `WT_THREAD_ACTIVE`, and `WT_THREAD_PANIC_FAIL`.
- `__thread_run` is the wrapper loop for every worker. It waits while inactive, clears per-thread error log state, calls the configured run callback, invokes an optional stop callback, and panics the connection for unrecoverable utility-thread failures when requested.
- `__thread_group_resize` and public `__wt_thread_group_resize` enforce `min <= max`, shrink before growth, grow the pointer array when needed, open one internal session per new thread, allocate the thread condition, create OS threads inactive, and activate up to `new_min`.
- `__thread_group_shrink` clears active/run flags above the new count, signals their conditions, joins threads without holding the group lock, closes sessions, destroys conditions, and frees slots.
- `__wt_thread_group_create`, `__wt_thread_group_destroy`, `__wt_thread_group_start_one`, `__wt_thread_group_stop_one`, and `__wt_thread_group_foreach` expose lifecycle, active-count control, and per-thread callbacks.

## Control Flow and State
Creation initializes lock and wait condition, records callbacks/name, then delegates to resize under the write lock. Resize first shrinks down to the new maximum so excess OS threads are stopped before allocation metadata changes. New slots are initialized from the old maximum to the new maximum and are launched with `WT_THREAD_RUN` set but without `WT_THREAD_ACTIVE`; the wrapper will sleep on `pause_cond` until activated. `current_threads` is an atomic count of active slots and doubles as the next start/stop index. Start increments it with `__wt_atomic_fetch_add_uint32`, marks that slot active, and signals the thread. Stop decrements it with `__wt_atomic_sub_uint32`, clears active, and signals the pause condition so the worker can re-check state.

## State and Persistence Behavior
This module is entirely in-memory. Persistence is indirect: utility threads may belong to subsystems such as eviction, checkpointing, or tiered storage that perform persistent work. The module's durable correctness role is ensuring those subsystem threads start, pause, shut down, and clean up consistently. Each thread has a dedicated internal session, so session lifecycle must match thread lifecycle exactly.

## Dependencies and Integration Points
The code depends on WiredTiger internal synchronization, atomics, condition variables, session management, verbose logging, and panic/error helpers. Subsystems integrate by supplying `chk_func`, `run_func`, and `stop_func`. `WT_THREAD_CAN_WAIT` controls whether internal sessions are opened with `WT_SESSION_CAN_WAIT`; `WT_THREAD_PANIC_FAIL` escalates callback failure to a connection panic.

## Risks and Edge Cases
Resizing is sensitive because it joins without the lock to avoid deadlock with threads that may need the group lock. Start/stop index arithmetic depends on `current_threads` and the invariant that active threads occupy the low slots. Error handling during resize is intentionally fatal: partial allocation failure destroys the group and panics, because a half-resized utility group can leave important background services inconsistent. `foreach` documents undefined behavior if called while threads are doing work and has a TODO to enforce this.

## Test Signals
Useful coverage includes create/destroy at min/max boundaries, resize growth and shrink with active workers sleeping on long condition waits, callback failure with and without panic flag, repeated start/stop respecting min/max, and sanitizer runs around lock handoff in shrink. Integration tests should watch for leaked internal sessions, stuck joins, missed condition signals, and active-count statistics during subsystem shutdown.
