# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_queue.c

## Purpose
Implements the per-leaf ZFS vdev I/O scheduler. It classifies queued I/O by priority, enforces per-class and aggregate concurrency limits, adjusts async-write concurrency based on dirty data, orders queued I/O by timestamp or LBA, aggregates adjacent I/Os, and issues more work as active I/Os complete.

## Queue Classes And Tunables
The queueable priorities include sync read/write, async read/write, scrub, removal, initializing, and trim. Tunables define min/max active counts per class, aggregate max active count, async-write dirty-data thresholds, aggregation size/gap limits, allocator queue-depth threshold, and optional TRIM aggregation.

## Main Data Structures
- Each `vdev_queue_t` has a mutex, active offset tree, per-type offset trees for reads/writes/TRIMs, and per-priority class trees.
- Sync read/write and TRIM class trees are timestamp ordered for latency consistency.
- Async, scrub, removal, and initializing class trees are LBA ordered.

## Key Functions
- `vdev_queue_init()` creates AVL trees and sets FIFO-vs-offset comparators for each priority.
- `vdev_queue_io_add()` and `vdev_queue_io_remove()` maintain queued class/type trees and SPA waitq kstats.
- `vdev_queue_pending_add()` and `vdev_queue_pending_remove()` maintain active counts/tree and SPA runq/kstat I/O accounting.
- `vdev_queue_max_async_writes()` linearly interpolates allowed async writes between min/max active based on `dp_dirty_total`, using max when sync tasks are pending.
- `vdev_queue_class_to_issue()` first finds a nonempty class below its minimum active count; if none, finds one below its maximum; it also respects `zfs_vdev_max_active`.
- `vdev_queue_aggregate()` expands around a candidate I/O through same-type, same inherited flags, sufficiently adjacent I/Os. Reads can bridge read gaps; writes can include optional I/Os and optionally stretch through optional gaps to improve device-level aggregation.
- `vdev_queue_io_to_issue()` selects the next priority, chooses the I/O after the last issued offset for LBA queues or oldest timestamp for FIFO queues, aggregates when possible, drops NODATA optional I/Os, and marks issued I/O active.
- `vdev_queue_io()` normalizes priority based on I/O type, adds `DONT_CACHE` and `DONT_QUEUE`, queues the zio, and may return an immediately issuable zio or start an aggregate.
- `vdev_queue_io_done()` removes completed active I/O, records latency, then issues as many newly eligible I/Os as possible.
- `vdev_queue_change_io_priority()` reprioritizes queued or not-yet-queued I/Os but not active I/Os.

## Important Behavior And Invariants
- Aggregated reads copy data from the aggregate ABD back into each parent on completion; writes copy each child write payload into the aggregate ABD before dispatch.
- Optional/NODATA I/Os are used to preserve write continuity and are completed without physical dispatch when selected alone.
- `vdev_queue_length()` and `vdev_queue_last_offset()` are intentionally lock-free approximations for load calculations.
- Priority is sanitized so child I/Os inherited from parents still land in a valid class for their read/write/TRIM type.

## Dependencies
Uses AVL trees, SPA I/O kstats, ZIO child/aggregate helpers, ABD copy/zero helpers, dirty-data state from the DSL pool, and queue state embedded in `vdev_t`.
