# File Research: sources/os/linux/linux/block/blk.h

## Scope

This is the central private block-layer header. It collects internal constants, structure declarations, inline helpers, and cross-file prototypes for queue lifetime, bio splitting/merging, elevators, partitions, disk events, zoned devices, integrity, debugfs, timekeeping, and block device open/ioctl paths.

## Major Interfaces

- Queue/request lifetime:
  - Queue freeze/unfreeze and drain prototypes, `blk_try_enter_queue()`, `bio_queue_enter()`, and `blk_wait_io()`.
  - Request timeout declarations `blk_rq_timeout()` and `blk_add_timer()`.
  - Optimized request reference helpers: `req_ref_inc_not_zero()`, `req_ref_put_and_test()`, `req_ref_set()`, and `req_ref_read()`.
- Flush and merge:
  - `struct blk_flush_queue`, `is_flush_rq()`, flush queue allocation/free, and `blk_insert_flush()`.
  - Merge predicates including `rq_mergeable()`, `blk_discard_mergable()`, `blk_rq_get_max_segments()`, and `blk_queue_get_max_sectors()`.
  - Bio/request merge prototypes and plug flush limits.
- Splitting/limits:
  - `bio_may_need_split()` and `__bio_split_to_limits()` route reads/writes, zone append, discard/secure erase, and write zeroes to operation-specific split helpers.
  - `get_max_segment_size()`, `bvec_gap_to_prev()`, and physical/zone-device compatibility helpers enforce DMA and segment constraints.
- Optional subsystems:
  - Integrity helpers compile to real functions or stubs depending on `CONFIG_BLK_DEV_INTEGRITY`.
  - Zoned helpers compile to real functions or stubs depending on `CONFIG_BLK_DEV_ZONED`.
  - Fault injection hooks compile according to fault-injection config.
- Disk/block device management:
  - Prototypes for partition add/delete/resize, disk allocation, queue allocation, partition scanning, block ioctl/uring command paths, truncation, bdev open/release/permission, independent access ranges, and disk events.
- Debug/time helpers:
  - `blk_time_get_ns()` caches a timestamp in the current plug for task-context block operations.
  - Debugfs lock helpers combine `debugfs_mutex` with `memalloc_noio_save()` to prevent reclaim recursion.

## Dependencies and Invariants

- This header is included by many block core files, so it keeps optional features behind static inline stubs to avoid scattering ifdefs.
- `blk_try_enter_queue()` must respect PM-only queues and uses percpu ref RCU acquisition.
- Merge helpers forbid passthrough, flush, write-zeroes, zone append, and `REQ_NOMERGE`/`RQF_NOMERGE` requests from normal merging.
- P2PDMA pages from different pgmaps must not be mixed in the same bio because the DMA map iterator caches mapping state from the first segment.
- Debugfs helpers must be used around block debugfs operations that could otherwise enter reclaim and recurse into a frozen queue.
