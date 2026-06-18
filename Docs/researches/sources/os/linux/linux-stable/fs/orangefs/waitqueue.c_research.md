# File Research: sources/os/linux/linux-stable/fs/orangefs/waitqueue.c

## Scope

This file implements in-kernel queuing and completion waiting for OrangeFS operations submitted to the userspace client-core daemon. It handles request list insertion, daemon wakeup, interruption, purge/retry after daemon exit, timeout handling, cancellation, and cleanup of abandoned operations.

## Public And Internal APIs Covered

- `purge_waiting_ops()` marks all queued request-list operations purged when the device closes.
- `service_operation()` submits an operation and waits for a matching downcall.
- `orangefs_cancel_op_in_progress()` converts an in-progress operation into a cancel request.
- Internal helpers: `orangefs_clean_up_interrupted_operation()` and `wait_for_matching_downcall()`.

## Control Flow And Behavior

- `service_operation()` stamps the operation with current pid/tgid, optionally acquires `orangefs_request_mutex`, initializes status, queues the operation on `orangefs_request_list`, marks it waiting, wakes daemon waiters, and releases the mutex before sleeping.
- Priority operations are inserted at the head of the request list. This is used for remount operations after client restart.
- If the daemon is not in service, normal operations wait only up to `op_timeout_secs`; unmount operations avoid waiting.
- Completion waits use `wait_for_completion_io_timeout()` for writeback, interruptible timeout for interruptible operations, and killable timeout otherwise.
- Successful downcalls are normalized through `orangefs_normalize_to_errno()` before returning.
- Interrupted, timed-out, or purged operations are marked `OP_VFS_STATE_GIVEN_UP` and removed from whichever list owns them: pending request list, in-progress hash list, or copy-to/from-daemon transient state.
- Purged operations may retry up to `ORANGEFS_PURGE_RETRY_COUNT`; shared-memory I/O operations return to their caller for retry because buffer ownership is involved.
- `orangefs_cancel_op_in_progress()` preserves the old tag as the cancel target, frees the shared-memory slot later, assigns a new tag to the cancel op, and queues it if the daemon is active.

## State And Data Structures

- Global synchronization: `orangefs_request_mutex`, `orangefs_request_list_lock`, `orangefs_request_list_waitq`, and `orangefs_htable_ops_in_progress_lock`.
- Per-operation state includes `op_state`, `list`, `lock`, `waitq`, `attempts`, `tag`, `slot_to_free`, `uses_shared_memory`, `upcall`, and `downcall`.

## Dependencies

- Relies on OrangeFS device code to move operations from request list to in-progress table, copy upcalls/downcalls, set serviced state, and complete `op->waitq`.
- Uses OrangeFS daemon service-state helpers and operation state macros from kernel headers.

## Risks And Invariants

- `wait_for_matching_downcall()` returns with `op->lock` held, and callers must release or pass it to cleanup exactly as documented.
- Cleanup must distinguish list-empty copy races from waiting and in-progress states to avoid freeing or reusing an operation while daemon copy is active.
- `ORANGEFS_OP_NO_MUTEX` is only safe when the caller already holds the request mutex.
- Cancellation requires the original operation still be in progress; otherwise the cancel request is not queued.
