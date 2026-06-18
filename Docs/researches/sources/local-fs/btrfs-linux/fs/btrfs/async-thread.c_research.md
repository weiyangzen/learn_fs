# File Research: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.c

Btrfs wrapper around Linux workqueues with optional ordered completion and adaptive concurrency.

Key points:
- Defines `struct btrfs_workqueue`, wrapping a normal kernel workqueue plus Btrfs owner, ordered-list state, pending count, active limit, current active workers, and threshold tracking.
- `btrfs_alloc_workqueue()` creates a named `btrfs-%s` workqueue.
- Threshold behavior:
  - Threshold `0` becomes default `32`.
  - Thresholds below default disable adaptive thresholding.
  - Larger thresholds start with `max_active=1` and grow/shrink based on pending work.
- `btrfs_alloc_ordered_workqueue()` creates a strictly ordered workqueue with max active `1`.
- `btrfs_workqueue_normal_congested()` reports congestion when pending work exceeds twice the threshold.
- `thresh_queue_hook()` increments pending count in queue context, including IRQ-safe context.
- `thresh_exec_hook()` decrements pending count and adjusts `workqueue_set_max_active()` from worker context.
- Ordered work:
  - `run_ordered_work()` walks `ordered_list` and only runs ordered callbacks after each item’s normal work is done.
  - Uses memory barriers pairing `smp_mb__before_atomic()` with `smp_rmb()` so ordered callbacks see normal-work writes.
  - Handles lifetime carefully so a currently executing work item is not recycled before ordered cleanup completes.
- `btrfs_work_helper()` runs the normal callback, marks ordered work done, and invokes ordered sequencing or direct final tracing.
- Public helpers initialize, queue, flush, set max, and destroy Btrfs workqueues.

Role in system:
- Provides Btrfs-specific async execution semantics used by I/O, checksumming, compression, and other background work.
- Ordered callback support is important where completion order must match queue order even if worker execution is parallel.
