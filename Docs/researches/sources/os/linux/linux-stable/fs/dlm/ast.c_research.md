# File Research: sources/os/linux/linux-stable/fs/dlm/ast.c

## Purpose

`ast.c` handles DLM AST/BAST callback creation, suppression, queuing, execution, suspension, and resumption for lockspaces.

## Main Responsibilities

- Executes completion AST callbacks and blocking AST callbacks.
- Suppresses redundant callbacks with `dlm_may_skip_callback()`.
- Allocates and fills `struct dlm_callback` objects for queued callbacks.
- Routes callbacks to userspace lock holders through `dlm_user_add_ast()`.
- Runs callbacks immediately, through an ordered workqueue, or through a delayed list depending on lockspace flags.
- Starts/stops callback workqueues for filesystem lockspaces.
- Suspends callback delivery during recovery and resumes delayed callbacks in bounded batches.

## Key Control Flow

- `dlm_add_cb()` is the main entry point.
- For userspace locks, it hands off to `dlm_user_add_ast()`.
- For kernel locks, it first checks whether a callback may be skipped.
- If `LSFL_CB_DELAY` is set, it queues a prepared callback on `ls_cb_delay`.
- If `LSFL_SOFTIRQ` is set, it invokes the callback inline.
- Otherwise it queues work on `ls_callback_wq`.
- `dlm_callback_suspend()` sets delay mode and flushes outstanding work.
- `dlm_callback_resume()` drains delayed callbacks in batches of `MAX_CB_QUEUE`.

## Callback Suppression Rules

- BASTs can be skipped if the blocking mode is compatible with the last granted CAST mode.
- Consecutive BASTs are suppressed when the new mode is redundant or less restrictive under the PR/CW rule.
- CASTs update last granted mode and may request LVB copying for userspace locks when mode transition rules require it.

## Important Dependencies

- DLM lock/resource structures from `dlm_internal.h`.
- Lock mode compatibility from lock code.
- LVB transition table from `lvb_table.h`.
- Callback allocation/freeing from memory helpers.
- Userspace AST routing from `user.h`.
- Tracepoints `trace_dlm_ast` and `trace_dlm_bast`.

## Edge Cases and Risks

- Callback delivery mode depends on lockspace flags; recovery paths must correctly suspend/resume to avoid callbacks during unstable state.
- Suppression relies on `lkb_last_*` state being updated consistently.
- Delayed callbacks are allocated objects and must be freed after execution.
- Inline softirq delivery bypasses workqueue context, so callback functions must be valid for that context.
