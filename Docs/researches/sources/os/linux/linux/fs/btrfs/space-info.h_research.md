# File Research: sources/os/linux/linux/fs/btrfs/space-info.h

## Scope And Role

`space-info.h` declares the public Btrfs space-info data model and reservation/reclaim API. It is the shared contract for logical space accounting, reservation flushing levels, reclaim state ordering, block-group membership, ticket lists, sysfs-visible reclaim counters, and helper updates for major counters.

The implementation is primarily in `space-info.c`, while many other Btrfs subsystems use this header to reserve, release, inspect, and reclaim filesystem space.

## Reservation Flush Modes

`enum btrfs_reserve_flush_enum` describes how much reclaim a caller may perform when a reservation cannot be admitted immediately.

Important modes:

- `BTRFS_RESERVE_NO_FLUSH`: fail quickly; used when flushing could deadlock or blocking is not allowed.
- `BTRFS_RESERVE_FLUSH_LIMIT`: run limited metadata reclaim, mainly delayed inode items and chunk allocation.
- `BTRFS_RESERVE_FLUSH_EVICT`: broader reclaim for eviction contexts.
- `BTRFS_RESERVE_FLUSH_DATA`: data reservation flushing, interruptible by fatal signals.
- `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE`: special data-space reclaim path for free-space inode work.
- `BTRFS_RESERVE_FLUSH_ALL`: full normal metadata reclaim.
- `BTRFS_RESERVE_FLUSH_ALL_STEAL`: full reclaim plus possible global reserve stealing.
- `BTRFS_RESERVE_FLUSH_EMERGENCY`: bypasses normal `bytes_may_use` pressure and admits if actual used space fits.

The comments document deadlock-sensitive contexts, especially transaction-handle holders.

## Reclaim States

`enum btrfs_flush_state` gives the ordered state machine used by metadata reclaim:

- Delayed inode item flushing.
- Delayed reference flushing.
- Delalloc flushing and ordered-extent waiting.
- Chunk allocation, including forced allocation.
- Delayed iputs.
- Transaction commit.
- Zoned reset and reclaim states.

The enum order is intentionally meaningful for `btrfs_async_reclaim_metadata_space()`.

## Space-Info Sub-Groups

`enum btrfs_space_info_sub_group` names:

- `BTRFS_SUB_GROUP_PRIMARY`
- `BTRFS_SUB_GROUP_DATA_RELOC`
- `BTRFS_SUB_GROUP_TREELOG`

`BTRFS_SPACE_INFO_SUB_GROUP_MAX` is `1`, so each primary space info currently has one sub-group slot. The implementation uses that slot for zoned data relocation under data space or treelog under metadata space.

## Main Type: `struct btrfs_space_info`

`struct btrfs_space_info` represents one logical allocation class.

Core identity and hierarchy:

- `fs_info`: owning filesystem.
- `parent`: parent primary space info for sub-groups.
- `sub_group[]`: child space-info slots.
- `subgroup_id`: primary, data relocation, or treelog.
- `flags`: block-group type flags.

Counters:

- `total_bytes`: logical bytes in this space class.
- `bytes_used`: bytes committed to extents.
- `bytes_pinned`: bytes freed but unavailable until transaction completion.
- `bytes_reserved`: bytes reserved by allocator for current allocations.
- `bytes_may_use`: optimistic reservations for delalloc and metadata work.
- `bytes_readonly`: bytes unavailable because block groups are readonly.
- `bytes_zone_unusable`: zoned-mode unusable bytes until zone reset.
- `disk_used` and `disk_total`: physical-disk accounting with mirrors/parity factors.

Allocation and reclaim state:

- `max_extent_size`: allocator ENOSPC hint.
- `chunk_size`: default chunk allocation size.
- `bg_reclaim_threshold`: fixed block-group reclaim threshold.
- `clamp`: preemptive reclaim threshold divisor shift.
- `full`: no more chunks can be allocated for this space.
- `chunk_alloc`: chunk allocation in progress.
- `flush`: async reclaim in progress.
- `force_alloc`: forced chunk allocation state.

Lists and synchronization:

- `lock`: protects counters, flags, reclaim state, tickets, and readonly block-group list.
- `groups_sem`: protects block-group lists by RAID type.
- `list`: links into `fs_info->space_info`.
- `ro_bgs`: readonly block groups.
- `priority_tickets` and `tickets`: reservation wait queues.
- `block_groups[BTRFS_NR_RAID_TYPES]`: block groups partitioned by RAID profile.

Ticket/reclaim metadata:

- `reclaim_size`: bytes needed for pending tickets.
- `tickets_id`: monotonic progress counter.
- `reclaim_count`, `reclaim_bytes`, `reclaim_errors`: sysfs-visible reclaim metrics.
- `dynamic_reclaim`, `periodic_reclaim`, `periodic_reclaim_ready`, `reclaimable_bytes`: background reclaim policy state.

Sysfs state:

- `kobj`
- `block_group_kobjs[]`

## Inline Helpers

`btrfs_mixed_space_info()` detects mixed data+metadata space infos.

`DECLARE_SPACE_INFO_UPDATE()` generates lock-held update helpers with tracing and underflow checks for:

- `bytes_may_use`
- `bytes_pinned`
- `bytes_zone_unusable`

`btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes. Callers must hold `space_info->lock`.

`btrfs_space_info_free_bytes_may_use()` subtracts may-use bytes and tries to grant tickets under the space-info lock.

`btrfs_space_info_type_str()` converts exact type combinations to `"SYSTEM"`, `"DATA+METADATA"`, `"DATA"`, `"METADATA"`, or `"UNKNOWN"`.

## Public API

Initialization and lookup:

- `btrfs_init_space_info()`
- `btrfs_add_bg_to_space_info()`
- `btrfs_update_space_info_chunk_size()`
- `btrfs_find_space_info()`
- `btrfs_clear_space_info_full()`

Diagnostics:

- `btrfs_dump_space_info()`
- `btrfs_dump_space_info_for_trans_abort()`

Reservation:

- `btrfs_reserve_metadata_bytes()`
- `btrfs_reserve_data_bytes()`
- `btrfs_try_granting_tickets()`
- `btrfs_can_overcommit()`

Reclaim:

- `btrfs_init_async_reclaim_work()`
- `btrfs_account_ro_block_groups_free_space()`
- `btrfs_space_info_update_reclaimable()`
- `btrfs_set_periodic_reclaim_ready()`
- `btrfs_calc_reclaim_threshold()`
- `btrfs_reclaim_sweep()`
- `btrfs_return_free_space()`

## Concurrency Notes

Most counter helpers require `space_info->lock`. The generated update helpers assert lock ownership and trace both logical counter updates and space reservation events.

Block-group list traversal requires `groups_sem`, while readonly block-group list accounting uses `space_info->lock` plus individual block-group locks.

Ticket list manipulation is lock-protected and coordinated with per-ticket locks in `space-info.c`.

## Integration Points

This header includes `trace/events/btrfs.h`, `linux/kobject.h`, wait queues, rwsems, spinlocks, and `volumes.h`. Its struct fields are used across reservation code, block-group management, sysfs allocation reporting, statfs, chunk allocation, and zoned reclaim.

## Risks And Edge Cases

The counter-update macro clamps underflow to zero after warning; callers should still treat underflow as a bug.

`btrfs_space_info_type_str()` switches on exact `flags`, so remap-tree or sub-group flags not matching listed combinations report `"UNKNOWN"`.

`BTRFS_SPACE_INFO_SUB_GROUP_MAX` being `1` means future additional sub-groups require ABI/code updates, not just enum additions.

## Testing Signals

Tests should validate:

- Underflow detection in generated update helpers.
- Correct `btrfs_space_info_used()` sums with and without `bytes_may_use`.
- Mixed profile detection.
- Type-string reporting for system, data, metadata, and mixed space.
- Ticket granting after may-use release.
- Reclaim threshold toggles through dynamic and periodic reclaim fields.
