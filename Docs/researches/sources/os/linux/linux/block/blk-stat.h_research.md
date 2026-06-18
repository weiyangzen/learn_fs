# File Research: sources/os/linux/linux/block/blk-stat.h

## Scope

This header declares the block-layer request latency statistics callback interface used by queue policies such as writeback throttling. It defines how a `request_queue` can collect per-request completion latency into bucketed per-CPU counters over a timed window and notify a policy callback.

## Core APIs

- `struct blk_stat_callback` is the central object: it carries an RCU list node, timer, per-CPU `blk_rq_stat` buckets, bucket selector, accumulated bucket array, callback function, private data, and RCU free head.
- Queue stats lifetime is exposed through `blk_alloc_queue_stats()` and `blk_free_queue_stats()`.
- Request completion accounting is exposed through `blk_stat_add(struct request *rq, u64 now)`.
- Accounting can be enabled without registering callbacks through `blk_stat_enable_accounting()` and `blk_stat_disable_accounting()`.
- Callback lifecycle is `blk_stat_alloc_callback()`, `blk_stat_add_callback()`, `blk_stat_remove_callback()`, and `blk_stat_free_callback()`.
- Timer helpers include `blk_stat_is_active()`, `blk_stat_activate_nsecs()`, `blk_stat_activate_msecs()`, and `blk_stat_deactivate()`.
- Bucket arithmetic helpers are `blk_rq_stat_add()`, `blk_rq_stat_sum()`, and `blk_rq_stat_init()`.

## Dependencies and Invariants

- Depends on block core types (`request`, `request_queue`, `blk_rq_stat`), Linux timers, jiffies conversion helpers, per-CPU storage, and RCU list lifetime.
- A callback is associated with only one queue at a time and must be removed before being freed.
- `bucket_fn()` returns a bucket index or `-1` to skip a request; users must provide a bucket count matching the allocated stats array.
- Deactivation uses `timer_delete_sync()`, so removal/free paths can rely on no concurrent timer callback after it returns.
