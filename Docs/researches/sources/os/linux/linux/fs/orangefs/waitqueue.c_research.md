# File Research: sources/os/linux/linux/fs/orangefs/waitqueue.c

## Role

Implements OrangeFS in-kernel operation queuing, waiting, timeout/retry behavior, interruption cleanup, and cancellation handoff to userspace client-core.

## Main Responsibilities

- `purge_waiting_ops()` marks queued operations purged when the userspace device is closing.
- `service_operation()` queues an operation on `orangefs_request_list`, wakes client-core, waits for a matching downcall, normalizes status to Linux errno, and retries purged operations when allowed.
- Supports priority operations for remount and `ORANGEFS_OP_NO_MUTEX` when request mutex is already held.
- Uses interruptible, killable, or I/O completion waits depending on flags.
- `orangefs_cancel_op_in_progress()` rewrites an in-progress I/O op into an `ORANGEFS_VFS_OP_CANCEL` request when cancellation is possible.
- `orangefs_clean_up_interrupted_operation()` marks interrupted operations as given up and removes them from the request list or in-progress hash table.
- `wait_for_matching_downcall()` translates completion, signal, purge, and timeout outcomes into success, `-EINTR`, `-EAGAIN`, `-EIO`, or `-ETIMEDOUT`.

## Important Control Flow

`service_operation()` fills pid/tgid, optionally takes `orangefs_request_mutex`, queues the op under list and op locks, wakes the daemon, and releases the mutex before waiting. If daemon service is unavailable, it uses a finite timeout except for unmount operations.

On success, the op lock is released and `downcall.status` is normalized. On failure, cleanup removes the op from whichever queue owns it and may retry if the op was purged and does not use shared memory.

## Dependencies

Uses OrangeFS global request list, in-progress hash, daemon service state, operation state bits, completions, and debug helpers.

## Research Notes

This file is the core concurrency bridge between synchronous VFS callers and asynchronous userspace servicing. Lock ordering and op-state transitions are the key invariants.
