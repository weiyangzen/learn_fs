# File Research: sources/os/linux/linux/fs/dlm/ast.c

## Role

Implements DLM AST/BAST callback dispatch, callback suppression, callback allocation, and lockspace callback workqueue control.

AST callbacks notify lock completion. BAST callbacks notify blocking conditions.

## Major Responsibilities

- Dispatches callbacks to kernel lock users.
- Skips redundant callbacks when safe.
- Allocates callback records for queued delivery.
- Routes user lock callbacks to DLM user handling.
- Supports immediate softirq callbacks or ordered workqueue callbacks.
- Suspends and resumes callback delivery during recovery-sensitive windows.

## Callback Dispatch

`dlm_run_callback()` handles actual callback invocation:

- For `DLM_CB_BAST`, traces `trace_dlm_bast()` and calls `bastfn(astparam, mode)`.
- For `DLM_CB_CAST`, traces `trace_dlm_ast()`, updates `lksb->sb_status` and `lksb->sb_flags`, then calls `astfn(astparam)`.

`dlm_do_callback()` runs a queued callback and frees the callback object.

`dlm_callback_work()` is the workqueue wrapper.

## Callback Suppression

`dlm_may_skip_callback()` avoids redundant callbacks:

- BAST callbacks can be skipped if the blocking mode is compatible with the last granted CAST mode.
- Consecutive BASTs for the same or more restrictive mode can be suppressed.
- CAST callbacks update last granted mode/time and may request LVB copying for user locks when mode transitions require it.

The function updates `lkb_last_*` tracking fields and optionally sets `copy_lvb`.

## Callback Allocation

`dlm_get_cb()` allocates a callback object and copies tracing/context fields:

- Lock ID.
- Lockspace global ID.
- Resource name and length.
- Callback flags, mode, status, and status-block flags.
- Lock status block pointer.

`dlm_get_queue_cb()` adds function pointers, ast parameter, and initializes the work item.

## Callback Submission

`dlm_add_cb()`:

- Sends user lock callbacks to `dlm_user_add_ast()`.
- Skips redundant callbacks via `dlm_may_skip_callback()`.
- If callbacks are delayed, queues them on `ls_cb_delay`.
- If softirq mode is enabled, runs callback directly.
- Otherwise queues callback work on `ls_callback_wq`.

Access to delay state is protected by `ls_cb_lock`.

## Workqueue Lifecycle

`dlm_callback_start()` creates an ordered high-priority reclaim-safe workqueue for filesystem lockspaces unless softirq mode is used.

`dlm_callback_stop()` destroys it.

`dlm_callback_suspend()` sets `LSFL_CB_DELAY` and flushes the workqueue.

`dlm_callback_resume()` drains delayed callbacks in batches of 25, either executing directly in softirq mode or queuing to the workqueue. It clears delay state when the list is empty.

## Important Invariants

- User callbacks take a separate path through `dlm_user_add_ast()`.
- Filesystem callbacks may need ordered workqueue execution.
- Callback delay state is lockspace-wide.
- Suppression depends on remembered previous callback modes and flags.
- Delayed callback draining uses batching and `cond_resched()` for long queues.

## Research Notes

This file is a concurrency and notification layer rather than lock-state logic itself. The main correctness concerns are avoiding duplicate blocking notifications while preserving required CAST/BAST ordering and ensuring recovery can suspend callbacks safely.
