# File Research: sources/os/linux/linux-stable/fs/btrfs/space-info.h

This header defines Btrfs space-info data structures, reservation flush policy enums, reclaim state ordering, byte-counter helpers, and exported APIs for reservation and reclaim.

Major definitions:
- `enum btrfs_reserve_flush_enum` describes caller-permitted reclaim strength:
  - no flushing,
  - limited flushing,
  - eviction-oriented flushing,
  - data flushing,
  - free-space-inode data flushing,
  - full flushing,
  - full flushing with global-reserve stealing,
  - emergency reservation.
- `enum btrfs_flush_state` orders reclaim stages used by async metadata reclaim. The numeric order is semantically important.
- `enum btrfs_space_info_sub_group` defines primary, data relocation, and tree-log subgroup identifiers.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently `1`, so each primary space-info can have one subgroup slot.

`struct btrfs_space_info`:
- Represents allocation state for a logical space class such as DATA, METADATA, SYSTEM, or mixed DATA+METADATA.
- Tracks logical counters:
  - `total_bytes`,
  - `bytes_used`,
  - `bytes_pinned`,
  - `bytes_reserved`,
  - `bytes_may_use`,
  - `bytes_readonly`,
  - `bytes_zone_unusable`.
- Tracks disk-accounting counters:
  - `disk_used`,
  - `disk_total`.
- Stores allocation/reclaim state:
  - `full`,
  - `chunk_alloc`,
  - `flush`,
  - `force_alloc`,
  - `reclaim_size`,
  - `tickets_id`,
  - `clamp`,
  - `chunk_size`.
- Holds ticket queues:
  - `priority_tickets`,
  - `tickets`.
- Holds block-group lists by RAID type under `groups_sem`.
- Exposes reclaim stats and policy:
  - `reclaim_count`,
  - `reclaim_bytes`,
  - `reclaim_errors`,
  - `dynamic_reclaim`,
  - `periodic_reclaim`,
  - `periodic_reclaim_ready`,
  - `reclaimable_bytes`.

Important inline helpers:
- `btrfs_mixed_space_info()` detects mixed DATA+METADATA space.
- `DECLARE_SPACE_INFO_UPDATE()` generates guarded counter update helpers with tracing and underflow detection.
- Generated helpers cover:
  - `bytes_may_use`,
  - `bytes_pinned`,
  - `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally `bytes_may_use`.
- `btrfs_space_info_free_bytes_may_use()` subtracts from `bytes_may_use` and immediately tries to grant tickets.
- `btrfs_space_info_type_str()` maps exact block group type flags to display strings.

Exported API surface:
- Initialization and lookup:
  - `btrfs_init_space_info()`,
  - `btrfs_add_bg_to_space_info()`,
  - `btrfs_update_space_info_chunk_size()`,
  - `btrfs_find_space_info()`,
  - `btrfs_clear_space_info_full()`.
- Reservation:
  - `btrfs_reserve_metadata_bytes()`,
  - `btrfs_reserve_data_bytes()`,
  - `btrfs_can_overcommit()`,
  - `btrfs_try_granting_tickets()`.
- Diagnostics:
  - `btrfs_dump_space_info()`,
  - `btrfs_dump_space_info_for_trans_abort()`.
- Reclaim:
  - `btrfs_init_async_reclaim_work()`,
  - `btrfs_account_ro_block_groups_free_space()`,
  - `btrfs_space_info_update_reclaimable()`,
  - `btrfs_set_periodic_reclaim_ready()`,
  - `btrfs_calc_reclaim_threshold()`,
  - `btrfs_reclaim_sweep()`,
  - `btrfs_return_free_space()`.

Concurrency assumptions:
- Byte counter helpers assert `space_info->lock` is held.
- Block-group list traversal is coordinated with `groups_sem`.
- The header exposes only policy and accounting interfaces; the reclaim state machine is implemented in `space-info.c`.
