# File Research: sources/os/linux/linux/fs/btrfs/async-thread.h

Purpose: Declares the public interface for Btrfs asynchronous workqueues.

Key types:
- `btrfs_func_t`: normal work callback.
- `btrfs_ordered_func_t`: ordered/free callback taking a boolean phase argument.
- `struct btrfs_work`: stores callbacks plus private kernel work item, ordered list entry, owner workqueue, and flags.

Public API:
- Allocation: `btrfs_alloc_workqueue()` and `btrfs_alloc_ordered_workqueue()`.
- Work lifecycle: `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_flush_workqueue()`, `btrfs_destroy_workqueue()`.
- Tuning/inspection: `btrfs_workqueue_set_max()`, `btrfs_work_owner()`, `btrfs_workqueue_owner()`, and `btrfs_workqueue_normal_congested()`.

Integration: Used by Btrfs worker paths that need filesystem-owned workqueue tracing, throttling, or ordered completion, including async checksum submission in `bio.c`.
