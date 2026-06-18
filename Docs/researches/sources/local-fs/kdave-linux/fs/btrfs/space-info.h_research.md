# File Research: sources/local-fs/kdave-linux/fs/btrfs/space-info.h

Read coverage: complete file, 344 lines.

This header defines the Btrfs space-info reservation and reclaim interface.

Main contents:
- `enum btrfs_reserve_flush_enum` defines caller flush permissions, from no-flush and limited flush through full flush, global-reserve stealing, and emergency reservation.
- `enum btrfs_flush_state` defines reclaim state ordering used by async metadata reclaim.
- `enum btrfs_space_info_sub_group` defines primary and zoned subgroups for data relocation and tree-log separation.
- `struct btrfs_space_info` stores logical/disk accounting, block-group lists, tickets, reclaim counters, sysfs kobjects, zoned unusable bytes, chunk sizing, and periodic reclaim state.

Important inline helpers:
- `btrfs_mixed_space_info()` detects mixed data+metadata space infos.
- `DECLARE_SPACE_INFO_UPDATE()` generates traced, underflow-checked update helpers for `bytes_may_use`, `bytes_pinned`, and `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes under lock.
- `btrfs_space_info_free_bytes_may_use()` releases may-use bytes and immediately retries ticket granting.
- `btrfs_space_info_type_str()` maps flags to user-readable type strings.

Exported API:
- Initialization and lookup: `btrfs_init_space_info()`, `btrfs_find_space_info()`.
- Block-group accounting: `btrfs_add_bg_to_space_info()`, `btrfs_update_space_info_chunk_size()`.
- Reservation: `btrfs_reserve_metadata_bytes()`, `btrfs_reserve_data_bytes()`, `btrfs_try_granting_tickets()`, `btrfs_can_overcommit()`.
- Diagnostics and reclaim: `btrfs_dump_space_info()`, `btrfs_dump_space_info_for_trans_abort()`, `btrfs_reclaim_sweep()`, `btrfs_calc_reclaim_threshold()`.
- Reclaim readiness: `btrfs_space_info_update_reclaimable()`, `btrfs_set_periodic_reclaim_ready()`, `btrfs_return_free_space()`.

Risk notes:
- Callers must hold `space_info->lock` for inline accounting helpers that assert lock ownership.
- Flush enum selection is a deadlock boundary: transaction-holding paths must avoid commit-capable flush modes.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently `1`, so subgroup users assume a single slot.
