# File Research: sources/os/linux/linux/block/blk-ioc.c

## Summary
Manages per-task block I/O contexts and optional per-queue `io_cq` associations used by block schedulers and I/O priority handling.

## Main Responsibilities
- Allocate, reference, share, and release `struct io_context`.
- Preserve I/O priority across task copy when appropriate.
- Implement permission and LSM checks for `set_task_ioprio()`.
- Manage `io_cq` objects that connect one `io_context` to one request queue.
- Tear down `io_cq` state on task exit or queue removal.

## Key APIs
- `put_io_context()`.
- `exit_io_context()`.
- `set_task_ioprio()`.
- `__copy_io()`.
- `ioc_clear_queue()`.
- `ioc_lookup_icq()`.
- `ioc_find_get_icq()`.

## Important Behavior
`io_context` has both `refcount` and `active_ref`. `active_ref` tracks task users; final active release exits all `io_cq`s before dropping the object reference.

With `CONFIG_BLK_ICQ`, `io_cq`s are stored in both an `ioc->icq_tree` indexed by queue id and queue-local `q->icq_list`. A cached RCU hint speeds issue-path lookup. Creation locks `q->queue_lock` before `ioc->lock`.

Release may need the reverse lock order while already holding queue-related locks, so final `io_cq` destruction can be punted to `system_power_efficient_wq`.

## State and Synchronization
Uses task locks for `task->io_context`, atomic reference counters, RCU for lookup hints and delayed `io_cq` freeing, `ioc->lock`, `q->queue_lock`, radix trees, and hlist/list membership.

## Risks
The lock ordering is subtle: destruction must coordinate `ioc->lock`, `q->queue_lock`, RCU protection, and queue lifetime. `set_task_ioprio()` has both credential and security-hook enforcement; bypassing it would skip intended authorization.
