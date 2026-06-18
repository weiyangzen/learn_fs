# File Research: sources/os/linux/linux/fs/btrfs/zoned.c

## Purpose
Implements Btrfs zoned block-device support. It discovers and validates zone geometry, manages superblock log zones, tracks empty and active zones, calculates block-group allocation pointers from device write pointers, enforces sequential metadata/data writes, supports zone append completion rewrites, reserves active zones for metadata/system/tree-log/data-relocation use, finishes or resets zones, and exposes zoned statistics.

## Zone Discovery and Validation
`btrfs_get_dev_zone_info_all_devices()` reads zone info for every opened device on zoned filesystems.

`btrfs_get_dev_zone_info()`:
- Allocates `struct btrfs_zoned_device_info`.
- Determines real zone size for zoned block devices or emulated zone size for regular devices.
- Rejects zone sizes outside 4 MiB to 8 GiB.
- Builds bitmaps for sequential zones, empty zones, and active zones.
- Optionally builds a zone cache for zoned devices.
- Reads zone reports in batches of `BTRFS_REPORT_NR_ZONES`.
- Tracks active-zone counts and enforces device active-zone limits.
- Validates superblock log zone pairs for each mirror.

Regular devices in a zoned filesystem are represented as emulated conventional zones by `emulate_report_zones()`.

`btrfs_check_zoned_mode()` verifies all devices use a common zone size, validates block queue limits, rejects mixed block groups, derives `max_zone_append_size`, sets `BTRFS_CHUNK_ALLOC_ZONED`, and validates zoned-incompatible mount options.

## Mount Options
`btrfs_check_mountopts_zoned()` rejects:
- space cache v1, because it is not COWed
- NODATACOW

It disables async discard for zoned mode.

## Superblock Log Zones
Zoned devices use two log zones per superblock mirror. Helpers:
- `sb_zone_number()` maps mirror index to zone number.
- `sb_write_pointer()` determines the current superblock write position from the two-zone state machine.
- `sb_log_location()` returns the read or write location and resets a full target zone before reuse.
- `btrfs_sb_log_location_bdev()` works before `btrfs_device` zone info is available.
- `btrfs_sb_log_location()` uses cached device zone info.
- `btrfs_advance_sb_log()` advances cached write pointers and finishes a full log zone.
- `btrfs_reset_sb_log_zones()` resets a mirror’s log-zone pair.

The state machine treats both zones empty as no superblock, both full as requiring generation comparison, and some partially used combinations as corruption.

## Allocatable Zone Selection and Empty-Zone Handling
`btrfs_find_allocatable_zones()` searches a physical hole for a zone-aligned region that:
- is empty when sequential
- does not overlap zoned superblock log zones
- does not overlap regular superblock bytenrs

`btrfs_ensure_empty_zones()` resets sequential zones in a free region when they are unexpectedly non-empty.

`btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks zones empty, and clears active-zone accounting.

## Block-Group Write Pointer Loading
`btrfs_load_block_group_zone_info()` is the central block-group initialization hook. It:
- Requires block-group length to be zone-size aligned.
- Finds and stores the physical chunk map in `cache->physical_map`.
- Loads per-stripe `zone_info` with physical location, capacity, and allocation offset.
- Counts sequential versus conventional stripes.
- Calculates `last_alloc` from the extent tree for conventional zones.
- Dispatches to profile-specific reconstruction.
- Sets `BLOCK_GROUP_FLAG_SEQUENTIAL_ZONE` when any stripe is sequential.
- Sets `alloc_offset`, `zone_capacity`, `meta_write_pointer`, active-list membership, and active runtime flags.

Profile-specific loaders:
- `btrfs_load_block_group_single()`: uses the single zone write pointer.
- `btrfs_load_block_group_dup()`: requires matching offsets across DUP stripes; data DUP requires raid-stripe-tree.
- `btrfs_load_block_group_raid1()`: handles mirrored profiles, missing devices, conventional zones, degraded mode, and active-zone mismatches.
- `btrfs_load_block_group_raid0()`: reconstructs striped allocation offset from per-stripe write pointers and validates stripe ordering/partial stripes.
- `btrfs_load_block_group_raid10()`: combines mirrored sub-stripes and RAID0 rows, validating mirror offset agreement and stripe ordering.
- RAID5/RAID6 are rejected.

For broken mirrored write pointers, some profiles mark the block group unallocatable by moving `alloc_offset` to `zone_capacity`.

## Free-Space Accounting
`btrfs_calc_zone_unusable()` computes:
- bytes already passed by the allocation pointer but not used
- capacity lost because zone capacity can be smaller than zone length

It marks the free-space cache finished and stores remaining sequential free space in `free_space_ctl->free_space`.

## Zone Append Data Writes
`btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` only for data writes in sequential-zone block groups. It avoids metadata, reads, non-zoned filesystems, and data relocation roots.

`btrfs_record_physical_zoned()` adjusts ordered checksum logical addresses after the device returns the actual physical append location.

`btrfs_finish_ordered_zoned()` finalizes ordered extents after zone append:
- Ignores preallocated/data-relocation writes.
- Walks ordered checksum ranges to detect non-contiguous actual logical placement.
- Splits ordered extents when append placement is fragmented.
- Rewrites the ordered extent and extent map disk bytenr when the final logical differs.
- Frees dummy checksum entries for NODATASUM/no-data-csum cases.

## Metadata Write Pointer Enforcement
`btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written at the current block-group metadata write pointer:
- Caches the current zoned block group in the write context.
- Allows writes exactly at `meta_write_pointer`.
- Activates metadata/system/tree-log block groups when active-zone tracking is enabled.
- Returns `-EAGAIN` for holes that transaction commit can fill.
- Returns `-EBUSY` when writeback should bail out.

`check_bg_is_active()` handles active metadata/system block-group pivoting, including waiting for prior extent-buffer writeback and finishing an old active block group.

## Active Zone Management
`btrfs_zone_activate()` activates all underlying zones for a block group, respecting per-device active-zone limits and reserved active zones. Activated block groups are linked into `fs_info->zone_active_bgs`.

`btrfs_can_activate_zone()` checks whether a future block-group allocation can activate enough zones for SINGLE or DUP profiles. Failure sets `BTRFS_FS_NEED_ZONE_FINISH`.

`btrfs_check_active_zone_reservation()` reserves active zones for metadata, tree-log, and system block groups, adjusting reservations for DUP profiles and already-active metadata/system groups.

## Zone Finishing
`do_zone_finish()` is the core finisher:
- Skips inactive groups.
- Refuses metadata finish if allocated metadata has not reached `meta_write_pointer`.
- Optionally marks the block group read-only and waits for reservations, ordered data, and metadata writeback.
- Clears active flags.
- Moves allocation pointers to capacity.
- Clears treelog/data-relocation tracking.
- Issues `REQ_OP_ZONE_FINISH` to sequential device zones.
- Releases active-zone accounting and list references.

Public finish paths:
- `btrfs_zone_finish()`
- `btrfs_zone_finish_endio()`
- `btrfs_schedule_zone_finish_bg()` and its workqueue function for metadata near zone end
- `btrfs_zone_finish_one_bg()` chooses an active data block group with least remaining space and finishes it
- `btrfs_zoned_activate_one_bg()` activates one metadata/system block group, optionally finishing a data group first

## Data Relocation Reservation
`btrfs_zoned_reserve_data_reloc_bg()` reserves a dedicated data relocation block group:
- Chooses the second empty data block group when possible.
- Migrates it to the data-relocation space-info subgroup.
- Allocates a new relocation block group if needed.
- Marks `fs_info->data_reloc_bg` and `BLOCK_GROUP_FLAG_ZONED_DATA_RELOC`.
- Activates the zone.

`btrfs_zoned_release_data_reloc_bg()` clears the relocation flag once the relocation write range reaches the block group allocation pointer.

## Zone Reset and Reclaim
`btrfs_reset_unused_block_groups()` resets fully zone-unusable unused block groups without deleting/recreating the block group. It chooses matching unused groups, resets each physical zone, restores `alloc_offset` to zero, updates `zone_unusable`, returns free space, and decrements `bytes_zone_unusable`.

`btrfs_zoned_should_reclaim()` compares device bytes used to total filesystem bytes and returns true once the configured reclaim threshold is reached.

`btrfs_free_zone_cache()` frees per-device cached zone reports after mount-time use.

## Device Replace Support
`btrfs_sync_zone_write_pointer()` synchronizes a replacement target’s write pointer by reading source-zone write pointer information and zero-filling the target gap. `read_zone_info()` maps logical addresses to mirrors and reads zone info from a working device, skipping missing/failing mirrors.

## Diagnostics
`btrfs_show_zoned_stats()` prints active block-group count, reclaimable/unused counts, reclaim need, data relocation/tree-log block-group IDs, and per-active-block-group write pointer, used, reserved, and unusable bytes.

## Concurrency and Locking
- `zone_active_bgs_lock` protects active block-group list membership.
- `block_group->lock` protects block-group runtime flags and allocation pointer fields.
- `zoned_meta_io_lock` serializes metadata/system active block-group pivoting.
- `dev_replace->rwsem` protects device-replace state while reading or finishing physical stripes.
- NOFS contexts wrap zone management/report operations that can be called inside filesystem allocation paths.

## Risk and Testing Signals
Important coverage:
- Superblock log two-zone state transitions and corruption cases.
- Mount-time reconstruction for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10.
- Mixed conventional/sequential devices.
- Degraded mirrored mounts with missing devices.
- Active-zone exhaustion and zone-finishing recovery.
- Zone append ordered-extent splitting/rewrite.
- Metadata write pointer hole handling.
- Data relocation block-group reservation/release.
- Reset of fully zone-unusable unused block groups.
