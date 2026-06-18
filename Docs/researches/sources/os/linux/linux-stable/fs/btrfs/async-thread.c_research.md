# File Research: sources/os/linux/linux-stable/fs/btrfs/async-thread.c

## Summary
Implements Btrfs workqueue wrappers with dynamic concurrency throttling and ordered completion callbacks.

## Main Responsibilities
- Allocates normal and ordered Btrfs workqueues.
- Initializes and queues `btrfs_work` items.
- Tracks pending work and adjusts max active workers.
- Provides ordered work completion in queue order.
- Flushes and destroys Btrfs workqueues.

## Important Behavior
Normal workqueues can start with low concurrency and grow or shrink based on pending work thresholds. The queue hook runs in IRQ-capable context and only updates counters; the execution hook runs in worker context and may call `workqueue_set_max_active()`.

Ordered work uses a separate ordered list. The normal work function runs first, sets `WORK_DONE_BIT` with a memory barrier, and `run_ordered_work()` invokes ordered callbacks in list order. The ordered callback receives `false` for completion and later `true` for freeing.

Special care prevents freeing and recycling the currently executing work item before all ordered dependencies are complete, preserving kernel workqueue non-reentrancy assumptions.

## Risks
Ordered work correctness depends on `WORK_DONE_BIT`, `WORK_ORDER_DONE_BIT`, list locking, and memory barriers. Threshold updates are intentionally approximate but must avoid calling sleepable workqueue APIs from queue-time contexts.
