# File Research: sources/local-fs/kdave-linux/fs/btrfs/async-thread.c

Purpose: Implements Btrfs-owned workqueue wrappers with optional ordered completion and dynamic concurrency thresholding.

Main structures:
- `struct btrfs_workqueue`: wraps a kernel `workqueue_struct`, owner `fs_info`, ordered-work list, spinlocks, pending count, maximum/current active worker counts, and threshold state.
- `struct btrfs_work`: declared in the header; stores normal and ordered callbacks plus list/workqueue state.

Workqueue creation:
- `btrfs_alloc_workqueue()` creates a normal named `btrfs-%s` workqueue. Thresholds below `DEFAULT_THRESHOLD` disable dynamic scaling; otherwise concurrency starts at 1 and grows toward `limit_active`.
- `btrfs_alloc_ordered_workqueue()` creates a strictly ordered kernel workqueue with `limit_active = current_active = 1`.

Execution flow:
- `btrfs_queue_work()` assigns the workqueue, updates pending threshold state, appends ordered work to `ordered_list` when needed, traces, and queues the kernel work.
- `btrfs_work_helper()` runs the normal callback, then either traces completion or marks `WORK_DONE_BIT` and calls `run_ordered_work()`.
- `run_ordered_work()` walks the ordered list only from the head, executes ordered callbacks in queue order, and uses `WORK_ORDER_DONE_BIT` as a barrier against duplicate ordered execution.

Concurrency and memory ordering:
- `thresh_queue_hook()` increments pending in queue/IRQ context.
- `thresh_exec_hook()` decrements pending in worker context and may call `workqueue_set_max_active()` after clamping current active workers.
- `smp_mb__before_atomic()` and `smp_rmb()` pair so ordered callbacks see writes done by normal callbacks before `WORK_DONE_BIT`.

Lifetime notes: Ordered callbacks have two phases: `ordered_func(work, false)` for ordered completion and `ordered_func(work, true)` for final freeing. The current work item is not freed until after `run_ordered_work()` is done to avoid kernel workqueue address-reuse deadlocks.

Risk notes: Ordered work correctness depends on list locking, memory barriers, and delayed freeing. Misusing `ordered_func(..., true)` or freeing a work item too early can race with ordered-list traversal.
