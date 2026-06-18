# File Research: sources/local-fs/kdave-linux/fs/btrfs/async-thread.h

Purpose: Public interface for Btrfs asynchronous workqueues.

Key types:
- `btrfs_func_t`: normal work callback.
- `btrfs_ordered_func_t`: ordered/free callback with a boolean phase argument.
- `struct btrfs_work`: callback fields plus private kernel work item, ordered list entry, owner workqueue, and flags.

Public API:
- Allocation: `btrfs_alloc_workqueue()` and `btrfs_alloc_ordered_workqueue()`.
- Work lifecycle: `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_flush_workqueue()`, `btrfs_destroy_workqueue()`.
- Tuning/inspection: `btrfs_workqueue_set_max()`, `btrfs_work_owner()`, `btrfs_workqueue_owner()`, `btrfs_workqueue_normal_congested()`.

Integration: Used by Btrfs async checksum submission in `bio.c` and by other filesystem worker paths that require ordered completion or filesystem ownership tracing.
