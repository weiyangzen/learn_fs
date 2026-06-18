# File Research: sources/os/linux/linux/block/blk-core.c

## Scope

This file is a central block-layer core implementation: request queue allocation/reference lifecycle, bio submission validation and recursion flattening, queue entry/freezing, block operation/status conversions, polling, disk I/O accounting, kblockd scheduling, plugging, and block subsystem initialization.

## Core APIs and Entry Points

- Queue state/lifecycle:
  - `blk_queue_flag_set()`, `blk_queue_flag_clear()`.
  - `blk_alloc_queue()`, `blk_get_queue()`, `blk_put_queue()`, `blk_queue_start_drain()`.
  - `blk_queue_enter()`, `__bio_queue_enter()`, `blk_queue_exit()`, `blk_sync_queue()`.
  - `blk_set_pm_only()`, `blk_clear_pm_only()`.
- Bio submission:
  - `submit_bio()`, `submit_bio_noacct()`, `submit_bio_noacct_nocheck()`.
  - Internal `__submit_bio()`, `__submit_bio_noacct()`, `__submit_bio_noacct_mq()`.
- Validation and remap:
  - `bio_check_ro()`, `bio_check_eod()`, `blk_partition_remap()`, `blk_check_zone_append()`, `blk_validate_atomic_write_op_size()`.
- Polling/accounting:
  - `bio_poll()`, `iocb_bio_iopoll()`.
  - `bdev_start_io_acct()`, `bio_start_io_acct()`, `bdev_end_io_acct()`, `bio_end_io_acct_remapped()`, `update_io_ticks()`.
- Plugging and workqueue:
  - `blk_start_plug_nr_ios()`, `blk_start_plug()`, `blk_finish_plug()`, `__blk_flush_plug()`, `blk_check_plugged()`.
  - `kblockd_schedule_work()`, `kblockd_mod_delayed_work_on()`.
- Initialization:
  - `blk_dev_init()` creates kblockd, queue slab cache, and block debugfs root.

## Major State

- `blk_debugfs_root`, exported block tracepoints.
- `blk_queue_ida` assigns queue ids used by blkcg lookup.
- `blk_requestq_cachep` allocates `struct request_queue`.
- `kblockd_workqueue` handles block async work.
- Operation-name and status conversion tables map `REQ_OP_*` and `BLK_STS_*`.

## Control Flow

- `submit_bio()` performs task/vm accounting and sets ioprio, then calls `submit_bio_noacct()`.
- `submit_bio_noacct()` checks NOWAIT support, crypto support, fault injection, read-only writes, end-of-device, partition remap, flush/FUA filtering, operation support, atomic write size, zone append constraints, and throttling before submission.
- `submit_bio_noacct_nocheck()` starts cgroup accounting and tracing, then either appends to `current->bio_list` during recursive submit or runs the mq/bio submit loop.
- Recursive submit loops convert recursive `submit_bio_noacct()` calls into iterative processing. For bio-based stacked drivers, newly submitted bios are sorted so lower-level queues are processed before same-level bios.
- `__submit_bio()` wraps actual submission in a plug, then either sends to blk-mq or calls `disk->fops->submit_bio()` after queue entry.
- Queue entry waits for freeze/PM resume unless NOWAIT is requested or the disk/queue is dying.
- `bio_poll()` can enter a frozen queue via direct percpu ref tryget to complete already submitted polled I/O during freezes.
- Plug flushing runs callbacks, flushes mq request lists, frees cached requests, and clears block timestamp state.

## Dependencies

- Block internals: blk-mq, sched, pm, cgroup/throttle/ioprio, integrity, crypto, part stats.
- Kernel subsystems: fault injection, debugfs, tracepoints, PM runtime, task I/O accounting, VM counters, workqueues.
- Disk/queue feature flags drive most validation decisions.

## Risks and Invariants

- `current->bio_list` recursion flattening is central to preventing stack overflows in stacked devices.
- Queue usage counters and freeze depth require ordering barriers to avoid missed wakeups.
- `REQ_OP_FLUSH` is not accepted directly as a bio op; flush bios enter as write with `REQ_PREFLUSH`.
- Metadata/swap/cgroup throttling and blk-crypto checks happen before actual lower-level submission.
- Plugging must be flushed on schedule/blocking paths to avoid reclaim and queue-freeze deadlocks.
