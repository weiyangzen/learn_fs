# File Research: sources/os/linux/linux/fs/btrfs/async-thread.c

Purpose: Implements Btrfs workqueue wrappers with filesystem ownership, optional ordered completion, tracing, and dynamic concurrency thresholding.

Main structures:
- `struct btrfs_workqueue`: wraps a kernel workqueue, owner `fs_info`, ordered work list, pending count, max/current active counts, threshold state, and locks.
- `struct btrfs_work`: declared in the header; contains normal and ordered callbacks plus embedded `work_struct`, list entry, owner queue, and flags.

Workqueue creation:
- `btrfs_alloc_workqueue()` creates a named `btrfs-%s` workqueue. Threshold values below `DEFAULT_THRESHOLD` disable dynamic scaling; otherwise active workers start at 1 and grow toward `limit_active`.
- `btrfs_alloc_ordered_workqueue()` creates a kernel ordered workqueue with `limit_active = current_active = 1` and thresholding disabled.

Execution flow:
- `btrfs_queue_work()` assigns the owner queue, applies queue threshold accounting, appends ordered work to `ordered_list`, traces, and queues the kernel work.
- `btrfs_work_helper()` runs the normal callback, then either traces completion or marks `WORK_DONE_BIT` and invokes ordered completion.
- `run_ordered_work()` walks only from the head of the ordered list, runs ordered callbacks in queue order, removes completed items, and invokes the final free phase.

Concurrency details:
- `thresh_queue_hook()` increments pending work count in queue/IRQ context.
- `thresh_exec_hook()` runs in worker context, decrements pending, occasionally adjusts max active workers with `workqueue_set_max_active()`, and clamps concurrency.
- `smp_mb__before_atomic()` and `smp_rmb()` ensure ordered callbacks see writes from normal callbacks before `WORK_DONE_BIT`.
- Current work is not freed until ordered traversal is done to avoid workqueue address-reuse deadlocks.

Public operations:
- Owner accessors: `btrfs_work_owner()` and `btrfs_workqueue_owner()`.
- Congestion check: `btrfs_workqueue_normal_congested()`.
- Lifecycle: `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_flush_workqueue()`, and `btrfs_destroy_workqueue()`.
- Tuning: `btrfs_workqueue_set_max()`.

Risk notes: Ordered completion correctness depends on list locking, memory barriers, and delayed freeing. Misusing the two-phase `ordered_func(work, do_free)` contract can race with list traversal or object lifetime.
