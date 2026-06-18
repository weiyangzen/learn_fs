# File Research: sources/os/linux/linux/block/disk-events.c

## Scope

This file implements disk event polling and notification for events such as media change and eject request. It manages per-disk event state, delayed polling work, sysfs attributes, uevents, and the global default poll interval parameter.

## Core State

- `struct disk_events` stores global list linkage, associated `gendisk`, spinlock, block mutex/depth, pending event mask, clearing mask, per-disk poll interval, and delayed work.
- Supported event strings/uevents are `media_change` and `eject_request`.
- `disk_events` global list is protected by `disk_events_mutex`.
- `disk_events_dfl_poll_msecs` is a module parameter under `block.events_dfl_poll_msecs`.

## Control Flow

- Blocking and scheduling:
  - `disk_block_events()` increments the block count and cancels delayed work for the first blocker.
  - `disk_unblock_events()` decrements the block count and schedules polling when it reaches zero.
  - `disk_flush_events()` merges a clearing mask and schedules immediate work if not blocked.
- Polling:
  - `disk_events_poll_jiffies()` chooses device-specific interval, default interval for `DISK_EVENT_FLAG_POLL`, or no polling.
  - `disk_check_events()` calls `disk->fops->check_events()`, filters already-pending events, records pending bits, reschedules polling, increments disk sequence on media change, and emits uevents when enabled.
  - `disk_events_workfn()` runs delayed polling.
- Synchronous clearing:
  - `disk_clear_events()` blocks normal polling, combines requested clear mask with racing flush clear mask, checks events synchronously, unblocks with immediate work if needed, and returns/clears pending bits.
  - `disk_check_media_change()` clears media/eject events and marks the disk for partition rescan when media changed.
  - `disk_force_media_change()` emits a media-change uevent, increments diskseq, and marks the whole device dead.
- Sysfs:
  - `events`, `events_async`, and `events_poll_msecs` expose supported events and per-disk polling interval.
  - Writes to `events_poll_msecs` block events, update interval, and unblock with immediate checking.
- Lifecycle:
  - `disk_alloc_events()`, `disk_add_events()`, `disk_del_events()`, and `disk_release_events()` allocate, start, stop, and free per-disk event tracking.

## Dependencies and Invariants

- Event checking requires `disk->fops->check_events` and nonzero `disk->events`.
- Blocking is counted; only the transition from zero to one cancels work, and only the final unblock reschedules it.
- `disk_clear_events()` intentionally ignores the block count for its synchronous check but serializes by temporarily blocking regular work.
- `disk_release_events()` expects `disk_del_events()` to have left the block count at one.
