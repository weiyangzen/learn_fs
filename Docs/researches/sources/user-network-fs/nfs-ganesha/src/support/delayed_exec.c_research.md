<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c -->
# sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c

## Purpose
This module implements NFS-Ganesha's delayed execution system: callers submit callbacks with nanosecond delays, and a detached executor thread runs them when their wall-clock deadline arrives.

## Important APIs, Types, and Functions
Internal types are `delayed_multi`, grouping all tasks for one `timespec`; `delayed_task`, carrying a callback and argument; and `delayed_thread`, tracking executor threads. Public APIs are `delayed_start`, `delayed_shutdown`, and `delayed_submit`. The worker entry point is `delayed_thread`, and `delayed_get_work` selects ready work from the AVL timer tree.

## Control Flow
`delayed_start` initializes mutex, condition variable, thread list, AVL tree, submission gates, and starts one detached executor thread. The thread registers with RCU, enables asynchronous cancellation, then loops while running: if no work exists it waits indefinitely, if future work exists it timed-waits until the earliest deadline, and if work is ready it removes one task, unlocks, executes the callback, and relocks. `delayed_submit` computes the deadline, inserts or reuses a tree node for that exact time, adds the task to the node list, and wakes the executor if the new task is earlier than the previous first node. `delayed_shutdown` blocks new submissions, waits for active submitters to drain, signals stop, waits up to 120 seconds for threads, then cancels any remaining thread.

## State and Persistence Behavior
State is process-local: a mutex, condition variable, AVL tree, task lists, thread list, `deny_submission`, `active_submitters`, and executor state. There is no durable persistence.

## Dependencies and Integration Points
It depends on pthreads, RCU bulletproof registration, project AVL/queue utilities, time helpers, atomic wrappers, logging, and memory wrappers. It integrates with subsystems that need deferred callbacks without owning their own timer thread.

## Risks and Test Signals
Risks include callback functions running on a shared executor and blocking all later delayed work, asynchronous cancellation hazards during forced shutdown, wall-clock time sensitivity if system time jumps, unchecked allocation failures through `gsh_malloc`, and lack of pending-task cleanup during shutdown after the executor exits. Test signals include ordering tests for earlier/later deadlines, multiple tasks with the same deadline, shutdown while submissions are active, callback blocking behavior, `EAGAIN` after shutdown starts, and sanitizer/thread-sanitizer runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c -->
