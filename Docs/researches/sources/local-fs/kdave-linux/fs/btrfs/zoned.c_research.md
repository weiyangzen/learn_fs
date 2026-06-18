# File Research: sources/local-fs/kdave-linux/fs/btrfs/zoned.c

## Role

`zoned.c` implements Btrfs zoned block device support. It handles zone discovery, zone caches, superblock log zones, allocation-pointer reconstruction, sequential-zone constraints, active-zone accounting, zone append integration, metadata write-pointer checks, data relocation reservations, zone finishing, zone reset/reclaim, and zoned statistics.

## Device Zone Discovery

`btrfs_get_dev_zone_info()` builds `struct btrfs_zoned_device_info` for each device when the filesystem has the zoned incompat flag. It supports both real zoned devices and regular devices under zoned emulation.

Key behavior:

- Real zoned devices use `bdev_zone_sectors()`.
- Non-zoned devices emulate conventional zones, with zone size derived from existing device extents if not already known.
- Zone sizes must be power-of-two, at least 4 MiB, at most 8 GiB, and consistent across devices.
- Bitmaps track sequential zones, empty zones, and active zones.
- Optional `zone_cache` stores reported `blk_zone` data for real zoned devices.
- Active-zone limits are checked against device limits or a default maximum.
- Superblock log zones are read and validated.

`btrfs_destroy_dev_zone_info()` frees bitmaps/cache. `btrfs_clone_dev_zone_info()` clones zone metadata for device replacement-related use while intentionally not cloning the cache.

## Zoned Mode Validation

`btrfs_check_zoned_mode()` rejects host-managed zoned devices unless the filesystem is zoned. In zoned mode it:

- Ensures all devices have equal zone size.
- Stacks queue limits from zoned block devices.
- Requires zone size alignment to `BTRFS_STRIPE_LEN`.
- Rejects mixed block groups.
- Sets `fs_info->zone_size`, `max_zone_append_size`, zoned chunk allocation policy, and maximum extent size.

`btrfs_check_mountopts_zoned()` rejects space cache v1 and `NODATACOW`, and disables async discard.

## Superblock Log Zones

Zoned devices use pairs of sequential zones for each superblock mirror. The code defines mirror locations at primary, 512 GiB, and 4 TiB offsets.

`sb_write_pointer()` interprets the two-zone log state machine, handling empty, in-use, full, and corrupted combinations. If both zones are full, it reads the final superblocks from both zones and chooses the older zone for the next write based on generation comparison.

`btrfs_sb_log_location_bdev()` and `btrfs_sb_log_location()` return read/write superblock locations. `btrfs_advance_sb_log()` updates cached superblock-zone state after writes and finishes full zones when needed. `btrfs_reset_sb_log_zones()` resets a superblock log zone pair.

## Allocation and Empty-Zone Handling

`btrfs_find_allocatable_zones()` finds an aligned, empty, superblock-free zone range inside a device hole. It avoids both zoned superblock log zones and regular superblock offsets.

`btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks zones empty, and clears active-zone bits.

`btrfs_ensure_empty_zones()` validates or resets zones in a free region before allocation. Non-empty sequential zones in free space trigger a warning and reset.

## Block Group Write Pointer Loading

`btrfs_load_block_group_zone_info()` reconstructs block group allocation state at mount or block group creation. It maps the logical block group to physical stripes, loads per-stripe zone state, and computes:

- `alloc_offset`
- `zone_capacity`
- `meta_write_pointer`
- sequential-zone runtime flags
- active block group list membership

For conventional-only mappings, it calculates the allocation pointer from the highest extent in the extent tree.

RAID-specific helpers enforce zoned write-pointer consistency:

- SINGLE requires a recoverable write pointer.
- DUP requires both copies to have matching offsets and requires raid-stripe-tree for data DUP.
- RAID1/RAID1C3/RAID1C4 tolerate missing devices only in degraded mode but otherwise require matching write pointers.
- RAID0 and RAID10 reconstruct logical allocation progress from stripe-row positions and reject stripe disorder, multiple partial stripes, or excessive stripe gaps.
- RAID5/RAID6 are rejected as unsupported in zoned mode.

Data block groups with non-SINGLE profiles require raid-stripe-tree.

## Zone Append and Ordered Extents

`btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` only for zoned data writes in sequential-zone block groups. It excludes reads, metadata, and data relocation roots.

`btrfs_record_physical_zoned()` adjusts checksum logical positions based on the actual physical address assigned by zone append.

`btrfs_finish_ordered_zoned()` handles completion after zone append. If zone append caused non-contiguous physical placement, it splits ordered extents and rewrites extent maps so final disk bytenrs match the actual append results. For nodatasum I/O it frees dummy checksum structures after using them to track logical addresses.

## Metadata Write Pointer Control

`btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written exactly at the block group metadata write pointer. It may activate a metadata/system block group, pivot away from a previously active metadata block group, finish the old group, or return:

- `0` when writing is allowed,
- `-EAGAIN` when a transaction commit should fill a hole,
- `-EBUSY` when writeback should bail out.

`check_bg_is_active()` contains the active metadata/system block group pivot logic and coordinates with `zoned_meta_io_lock`.

## Active Zone Accounting and Finishing

`btrfs_zone_activate()` marks a block group and its underlying zones active, respecting per-device `max_active_zones` and reserved active zones for metadata/system needs.

`do_zone_finish()` transitions an active block group to finished/full state. It can wait for reservations, ordered extents, and metadata writeback, marks allocation pointers at capacity, updates free space to zero, clears tree-log/data-relocation markers, issues `REQ_OP_ZONE_FINISH`, clears active zone bits, and removes the block group from the active list.

Public wrappers include:

- `btrfs_zone_finish()`
- `btrfs_zone_finish_endio()`
- `btrfs_schedule_zone_finish_bg()`
- `btrfs_zone_finish_one_bg()`
- `btrfs_zoned_activate_one_bg()`
- `btrfs_can_activate_zone()`

## Data Relocation and Reclaim

`btrfs_zoned_reserve_data_reloc_bg()` reserves a dedicated data relocation block group, preferring the second empty data block group or allocating a new one in the data relocation space-info subgroup.

`btrfs_zoned_release_data_reloc_bg()` clears the relocation runtime flag once all relocation extents are written.

`btrfs_zoned_should_reclaim()` compares used bytes against total bytes and the reclaim threshold.

`btrfs_reset_unused_block_groups()` resets fully unused, fully zone-unusable block groups in place, updating free-space and `bytes_zone_unusable` accounting without deleting/recreating the block group.

## Device Replace Support

`btrfs_sync_zone_write_pointer()` synchronizes a replacement target’s sequential-zone write pointer by reading source zone state and zero-filling the target from its current physical position to the source write pointer.

## Statistics

`btrfs_show_zoned_stats()` emits active block group counts, reclaimable/unused counts, reclaim need, data relocation/tree-log block group ids, and per-active-zone allocation/usage/reservation/unusable data.
