# File Research: sources/local-fs/btrfs-linux/fs/btrfs/space-info.h

This header defines Btrfs space-info state, reservation flush policies, reclaim states, subgroup identifiers, counter update helpers, and the public API for space reservation and reclaim.

Reservation flush policies:
- `BTRFS_RESERVE_NO_FLUSH` fails quickly and is used where flushing would block or deadlock, such as active transaction handles, nowait writes, and transaction attach/start cases that rely on existing reserves.
- `BTRFS_RESERVE_FLUSH_LIMIT` can run delayed inode items and allocate a chunk.
- `BTRFS_RESERVE_FLUSH_EVICT` can run delayed items, delayed refs, delalloc/ordered extents, chunk allocation, and transaction commit.
- `BTRFS_RESERVE_FLUSH_DATA`, `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE`, and `BTRFS_RESERVE_FLUSH_ALL` use broader reclaim; data/all waits are fatal-signal interruptible.
- `BTRFS_RESERVE_FLUSH_ALL_STEAL` is like full flushing but may steal from the global block reserve.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` is reserved for `btrfs_use_block_rsv()` fallback when pessimistic reservation sizing was insufficient.

Reclaim state ordering:
- `enum btrfs_flush_state` orders metadata async reclaim states from delayed item flushing through delayed refs, delalloc, chunk allocation, delayed iputs, transaction commit, zone reset, and zoned block group reclaim.
- The numeric order is significant for `space-info.c`'s reclaim state machine.

`struct btrfs_space_info`:
- Points to `fs_info`, optional parent, and at most one zoned subgroup.
- Tracks logical counters: `total_bytes`, `bytes_used`, `bytes_pinned`, `bytes_reserved`, `bytes_may_use`, `bytes_readonly`, and `bytes_zone_unusable`.
- Tracks allocator state: `max_extent_size`, `chunk_size`, `bg_reclaim_threshold`, `clamp`, `full`, `chunk_alloc`, `flush`, and `force_alloc`.
- Tracks mirrored disk accounting with `disk_used` and `disk_total`.
- Owns lists for readonly block groups, priority tickets, normal tickets, and per-RAID block groups.
- Maintains `reclaim_size` and `tickets_id` for ticket-driven reclaim progress.
- Provides sysfs kobjects for the space info and its block-group profile directories.
- Maintains reclaim statistics: `reclaim_count`, `reclaim_bytes`, and `reclaim_errors`.
- Controls automatic block-group reclaim through `dynamic_reclaim`, `periodic_reclaim`, `periodic_reclaim_ready`, and `reclaimable_bytes`.

Subgroups:
- `BTRFS_SUB_GROUP_PRIMARY` identifies ordinary space infos.
- `BTRFS_SUB_GROUP_DATA_RELOC` and `BTRFS_SUB_GROUP_TREELOG` are used for zoned-mode data relocation and tree-log metadata.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently one, so each primary can have at most one subgroup.

Inline helpers:
- `btrfs_mixed_space_info()` detects combined DATA+METADATA space.
- `DECLARE_SPACE_INFO_UPDATE()` generates locked counter update helpers with tracepoints and underflow protection.
- Generated helpers update `bytes_may_use`, `bytes_pinned`, and `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes.
- `btrfs_space_info_free_bytes_may_use()` subtracts may-use bytes and immediately tries to grant waiting tickets.
- `btrfs_space_info_type_str()` maps common space-info flags to SYSTEM, DATA+METADATA, DATA, METADATA, or UNKNOWN.

Exported API:
- Initialization and lookup: `btrfs_init_space_info()`, `btrfs_add_bg_to_space_info()`, `btrfs_update_space_info_chunk_size()`, `btrfs_find_space_info()`, `btrfs_clear_space_info_full()`.
- Diagnostics: `btrfs_dump_space_info()` and `btrfs_dump_space_info_for_trans_abort()`.
- Reservations: `btrfs_reserve_metadata_bytes()`, `btrfs_reserve_data_bytes()`, `btrfs_try_granting_tickets()`, and `btrfs_can_overcommit()`.
- Reclaim work: `btrfs_init_async_reclaim_work()`, `btrfs_space_info_update_reclaimable()`, `btrfs_set_periodic_reclaim_ready()`, `btrfs_calc_reclaim_threshold()`, `btrfs_reclaim_sweep()`, and `btrfs_return_free_space()`.
- Reporting: `btrfs_account_ro_block_groups_free_space()`.

Cross-file relationships:
- Implemented by `space-info.c`.
- Included by allocation, transaction, block reserve, delalloc, block-group, sysfs, and superblock code.
- Includes `volumes.h` because space infos organize block groups by RAID profile and use Btrfs block-group flags.

Important invariants:
- Callers of generated update helpers and `btrfs_space_info_used()` must hold `space_info->lock`.
- `bytes_may_use` is reservation accounting, not actual allocated extent use.
- `bytes_zone_unusable` is a first-class used component for zoned filesystems until zone reset makes it reusable.
- The header's enum order and public flush semantics are part of the contract with `space-info.c`; changing them changes reclaim behavior.
