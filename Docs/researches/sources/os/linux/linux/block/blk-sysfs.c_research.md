# File Research: sources/os/linux/linux/block/blk-sysfs.c

## Scope

This file implements `/sys/block/<disk>/queue/` attributes, the queue kobject type, and queue registration/unregistration with sysfs and debugfs. It is the table-driven bridge between user-visible queue knobs and request queue limits, elevator state, rq-qos/WBT state, zoned flags, and block crypto/independent access range sysfs children.

## Core APIs and Entry Points

- `struct queue_sysfs_entry` abstracts queue attributes with normal `show/store` callbacks or queue-limit `show_limit/store_limit` callbacks.
- Generic helpers parse and print numeric values: `queue_var_show()`, `queue_var_store()`, and WBT-specific `queue_var_store64()`.
- Mutable request-queue attributes:
  - `queue_requests_store()` updates `q->nr_requests` under `tag_set->update_nr_hwq_lock`, freezes the queue, and updates scheduler tags.
  - `queue_async_depth_store()` freezes the queue, updates `q->async_depth`, and calls elevator `depth_updated()`.
  - `queue_ra_store()` writes `disk->bdi->ra_pages` under `q->limits_lock`.
  - `queue_nomerges_store()`, `queue_rq_affinity_store()`, `queue_io_timeout_store()`, `queue_zoned_qd1_writes_store()`, and `queue_poll_store()` update queue flags or timeout policy.
- Queue-limit attributes are committed through `queue_limits_start_update()` and `queue_limits_commit_update_frozen()` for fields such as max sectors, discard limits, write zeroes limits, feature flags, write cache mode, rotational state, iostats, add_random, stable_writes, and passthrough iostats.
- `queue_attr_show()` and `queue_attr_store()` dispatch sysfs operations, adding `q->limits_lock` protection for `show_limit` and using the queue limits update transaction for `store_limit`.
- `blk_register_queue()` creates the queue kobject, registers mq sysfs/debugfs state, sets zoned defaults, registers independent access ranges and crypto sysfs, selects the default elevator, enables WBT, emits uevents, and switches the usage counter to percpu mode.
- `blk_unregister_queue()` clears `QUEUE_FLAG_REGISTERED`, removes mq/crypto sysfs children, removes independent access ranges, deletes the queue kobject, tears down the elevator, and removes debugfs.

## Attribute Layout

- `queue_attrs` contains common bio/request queue attributes, with comments separating `q->limits_lock` protected attributes from lockless ones.
- `blk_mq_queue_attrs` contains mq-only attributes: scheduler, `nr_requests`, `async_depth`, WBT latency, rq affinity, and I/O timeout.
- Visibility filters hide zoned-only attributes for non-zoned queues, hide mq attributes for non-mq queues, and hide `io_timeout` when the mq driver has no timeout callback.

## Dependencies and Invariants

- Uses sysfs/kobject infrastructure, blk-mq sysfs/debugfs, elevator switching, queue limit update APIs, WBT, blk-cgroup/throttle headers, blk crypto sysfs, and block tracing shutdown.
- `queue_requests_store()` uses `down_write_trylock()` to avoid a documented kernfs active-reference deadlock during disk deletion.
- Queue-limit stores must not mutate live limits directly; they operate on a copy and commit through the frozen update path.
- Debugfs creation/removal is serialized by block debugfs helpers to avoid reclaim recursion while queues are frozen.
