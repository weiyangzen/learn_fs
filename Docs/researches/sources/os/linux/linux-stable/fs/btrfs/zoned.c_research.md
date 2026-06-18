# File Research: sources/os/linux/linux-stable/fs/btrfs/zoned.c

## Purpose

`zoned.c` implements Btrfs zoned block device support. It discovers and caches zone geometry, validates zoned mount constraints, manages superblock log zones, tracks active zones, recovers block-group write pointers, enforces sequential write placement, coordinates zone append completion, finishes zones, reserves active-zone budget for metadata/system use, and supports zoned block-group reclaim/reset.

## Major Areas

### Zone Discovery and Device State

- `btrfs_get_dev_zone_info_all_devices()` loads zone information for all devices during mount.
- `btrfs_get_dev_zone_info()` allocates and populates `struct btrfs_zoned_device_info`.
  - Supports true zoned devices and regular devices with emulated conventional zones.
  - Validates zone size bounds: 4 MiB minimum and 8 GiB maximum.
  - Builds bitmaps for sequential zones, empty zones, and active zones.
  - Tracks `max_active_zones` and initializes `active_zones_left`.
  - Optionally creates a zone cache for real zoned devices.
  - Validates superblock log zone state.
- `btrfs_destroy_dev_zone_info()` and `btrfs_clone_dev_zone_info()` manage zone-info lifecycle.

### Zoned Mode Validation

- `btrfs_check_zoned_mode()` rejects zoned devices unless the filesystem has the zoned incompat flag.
- In zoned mode, all devices must have the same zone size.
- Queue limits are stacked from zoned block devices.
- Mixed block groups are rejected.
- `fs_info->zone_size`, `max_zone_append_size`, `max_extent_size`, and chunk allocation policy are configured.
- `btrfs_check_mountopts_zoned()` rejects space cache v1 and NODATACOW, and disables async discard.

### Superblock Log Zones

- Zoned devices store superblocks in log zone pairs at primary, 512 GiB, and 4 TiB mirror positions.
- `sb_write_pointer()` interprets the two-zone log state and chooses the current write pointer or latest full-zone superblock.
- `btrfs_sb_log_location_bdev()` and `btrfs_sb_log_location()` locate read/write superblock positions.
- `btrfs_advance_sb_log()` advances cached superblock log write pointers and finishes full zones.
- `btrfs_reset_sb_log_zones()` resets a mirror’s superblock log zone pair.

### Allocation Zone Selection and Reset

- `btrfs_find_allocatable_zones()` searches for empty sequential zones and avoids both zoned superblock log zones and regular superblock offsets.
- `btrfs_reset_device_zone()` resets device zones, marks them empty, and clears active-zone accounting.
- `btrfs_ensure_empty_zones()` validates allocation targets and forcibly resets non-empty sequential zones that should be free.

### Block Group Write Pointer Recovery

- `calculate_alloc_pointer()` derives an allocation pointer for conventional-zone block groups from the highest existing extent.
- `btrfs_load_zone_info()` reads each mapped device zone and derives physical position, capacity, active state, and allocation offset.
- Per-profile loaders validate and combine zone write pointers:
  - `btrfs_load_block_group_single()`
  - `btrfs_load_block_group_dup()`
  - `btrfs_load_block_group_raid1()`
  - `btrfs_load_block_group_raid0()`
  - `btrfs_load_block_group_raid10()`
- `btrfs_load_block_group_by_raid_type()` dispatches by profile and rejects unsupported RAID5/RAID6.
- `btrfs_load_block_group_zone_info()` attaches the chunk map, initializes `alloc_offset`, `zone_capacity`, `meta_write_pointer`, active-list membership, and sequential-zone flags.

Important profile constraints:
- Zoned data DUP/RAID profiles require raid-stripe-tree support.
- Mirrored profiles must have matching write pointer offsets unless degraded behavior allows missing devices.
- RAID0/RAID10 loaders reconstruct logical allocation progress from per-stripe write pointers and reject stripe disorder or multiple partial stripes.

### Sequential Data and Metadata IO

- `btrfs_calc_zone_unusable()` computes unusable space from written-but-free and capacity-shortfall regions.
- `btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` for normal data writes in sequential-zone block groups, excluding data relocation.
- `btrfs_record_physical_zoned()` adjusts checksum logical addresses after zone append returns the actual physical write location.
- `btrfs_finish_ordered_zoned()` splits or rewrites ordered extents when zone append caused physically non-contiguous placement.
- `btrfs_check_meta_write_pointer()` enforces metadata/system writes at `meta_write_pointer`, handles active metadata/system block-group pivoting, and returns `0`, `-EAGAIN`, or `-EBUSY`.

### Device Replace and Zone Pointer Sync

- `btrfs_zoned_issue_zeroout()` zeroes sequential-zone ranges.
- `btrfs_sync_zone_write_pointer()` advances a replacement target zone write pointer by zero-filling from the target position to the source zone write pointer.

### Active Zone Management and Zone Finish

- `btrfs_zone_activate()` activates a block group and its underlying zones while respecting per-device active-zone limits and reserved metadata/system capacity.
- `do_zone_finish()` finishes an active block group, waits for outstanding writes when needed, updates block-group allocation state to full, finishes device zones, clears special block-group references, and removes the group from the active list.
- `btrfs_zone_finish()` is the public wrapper.
- `btrfs_can_activate_zone()` checks whether active-zone budget exists for new allocation.
- `btrfs_zone_finish_endio()` finishes a block group when IO reaches the final allocatable range.
- `btrfs_schedule_zone_finish_bg()` schedules asynchronous zone finish after the last metadata extent buffer writes.

### Relocation, Reclaim, and Stats

- `btrfs_zoned_reserve_data_reloc_bg()` reserves or creates a data relocation block group and moves it into the relocation space-info subgroup.
- `btrfs_zoned_release_data_reloc_bg()` releases the relocation flag once all relocation extents are written.
- `btrfs_zone_finish_one_bg()` chooses an active data block group with least remaining space and finishes it.
- `btrfs_zoned_activate_one_bg()` tries to activate a metadata/system block group, optionally finishing another group first.
- `btrfs_check_active_zone_reservation()` reserves active-zone slots for metadata, tree-log, and system block groups.
- `btrfs_reset_unused_block_groups()` resets fully zone-unusable unused block groups so they can be reused without deleting/recreating chunks.
- `btrfs_show_zoned_stats()` emits active block group, reclaim, relocation, tree-log, and per-active-zone statistics.

## Important Invariants

- Zoned filesystems cannot use mixed block groups, NODATACOW, or space cache v1.
- Block group length and allocation targets must be aligned to zone size.
- Sequential zones must be written in order; metadata uses `meta_write_pointer`, while data can use zone append.
- Active-zone limits are tracked per device and can reserve capacity for metadata/system needs.
- Superblock log zones are special allocation exclusions.
- Missing/failing devices are represented during write-pointer recovery, but unrecoverable mismatches become mount-time errors or make block groups unallocatable.
- Zone finish transitions an active block group to full and clears active accounting on underlying device zones.

## Dependencies

This file depends on Linux zoned block APIs, zone management operations, queue limits, Btrfs chunk maps, block groups, device replace, transactions, sysfs, ordered extents, extent buffers, raid-stripe-tree assumptions, and filesystem-wide lock ordering.

## Research Notes

`zoned.c` is a central policy implementation for making Btrfs copy-on-write allocation compatible with sequential-write devices. The code bridges physical zone constraints with logical Btrfs block groups. Most complexity comes from recovering write pointers across RAID profiles, preserving metadata ordering, handling zone append relocation of physical writes, and managing scarce active-zone resources.
