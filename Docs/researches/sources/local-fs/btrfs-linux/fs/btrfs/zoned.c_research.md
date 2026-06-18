# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zoned.c

This file implements Btrfs zoned-mode support: device zone discovery, emulated zones for regular devices in zoned filesystems, superblock log-zone placement, active-zone accounting, block-group write-pointer recovery, sequential allocation state, zone append handling, metadata write-pointer enforcement, device-replace write-pointer synchronization, zone finishing, zoned data relocation block groups, reclaim decisions, unused block-group zone reset, and zoned statistics.

Major constants:
- `BTRFS_REPORT_NR_ZONES` limits one zone-report batch to 4096 zones.
- `WP_MISSING_DEV` and `WP_CONVENTIONAL` are pseudo write-pointer values for missing devices and conventional zones.
- Superblock log zones are anchored at 0, 512 GiB, and 4 TiB, each using two zones.
- `BTRFS_DEFAULT_MAX_ACTIVE_ZONES` supplies a default when devices expose no active-zone limit.
- `BTRFS_MIN_ACTIVE_ZONES` reserves enough active zones for superblock mirrors, system, metadata, data, tree-log, and relocation use.
- Supported zone sizes are constrained between 4 MiB and 8 GiB.

Device zone discovery:
- `btrfs_get_dev_zone_info_all_devices()` loads zone info for all open devices during mount when the incompat `ZONED` flag is present.
- `btrfs_get_dev_zone_info()` allocates `struct btrfs_zoned_device_info`, determines zone size, validates supported range, computes zone count, allocates sequential/empty/active bitmaps, optionally allocates a zone cache, reports zones, tracks active zones, validates superblock log zones, and stores max-active-zone state.
- Non-zoned devices in zoned filesystems are supported through `emulate_report_zones()`, which presents regular devices as conventional zones of the filesystem zone size.
- `calculate_emulated_zone_size()` derives emulated zone size from the first device extent when needed.
- `btrfs_get_dev_zones()` wraps cached reporting for real zoned devices and emulated reporting for regular devices.
- `btrfs_destroy_dev_zone_info()` frees bitmaps, zone cache, and the zone-info object.
- `btrfs_clone_dev_zone_info()` clones bitmap state for a replacement/clone device but intentionally drops the zone cache.

Zoned mode validation:
- `btrfs_check_zoned_mode()` rejects host-managed zoned devices when the filesystem is not zoned, enforces equal zone sizes across devices, stacks queue limits from zoned devices, checks zone-size stripe alignment, rejects mixed block groups, computes `max_zone_append_size`, switches chunk allocation policy to `BTRFS_CHUNK_ALLOC_ZONED`, bounds max extent size, and validates mount options.
- `btrfs_check_mountopts_zoned()` rejects space cache v1 and `NODATACOW`, and disables async discard for zoned mode.

Superblock log handling:
- `sb_write_pointer()` interprets the two-zone superblock log state machine, handles empty/full/in-use combinations, compares generations when both log zones are full, and detects corrupted states.
- `btrfs_sb_log_location_bdev()` computes the read/write superblock location directly from a block device, used before full Btrfs device state exists.
- `btrfs_sb_log_location()` does the same from a `btrfs_device`, using regular superblock offsets for zoned filesystems on non-zoned devices.
- `btrfs_advance_sb_log()` advances cached superblock log-zone state after a write and finishes a full log zone when necessary.
- `btrfs_reset_sb_log_zones()` resets both log zones for a mirror.

Zone allocation and reset helpers:
- `btrfs_find_allocatable_zones()` scans a device hole for an aligned region whose sequential zones are empty and that does not overlap zoned or regular superblock locations.
- `btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks each reset zone empty, and clears active-zone accounting.
- `btrfs_ensure_empty_zones()` validates or resets a free range before allocating it.
- `btrfs_zoned_issue_zeroout()` issues zeroout only for sequential zones.

Block-group write-pointer loading:
- `btrfs_load_block_group_zone_info()` is the central mount/new-block-group loader. It verifies zone alignment, finds and stores the physical chunk map, loads per-stripe zone state, detects conventional versus sequential stripes, reconstructs allocation offsets by RAID profile, initializes `meta_write_pointer`, and inserts active groups into `fs_info->zone_active_bgs`.
- `btrfs_load_zone_info()` loads one physical stripe’s zone info, handles missing devices, conventional zones, new block groups, device replace, offline/readonly/full/empty/partial zones, and active-zone bits.
- `calculate_alloc_pointer()` derives the allocation pointer for conventional-zone block groups from the highest-addressed extent item.
- `btrfs_load_block_group_by_raid_type()` dispatches profile-specific recovery for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10. RAID5/6 are rejected.
- `btrfs_load_block_group_single()` accepts one recovered write pointer.
- `btrfs_load_block_group_dup()` requires matching offsets across two stripes, normalizes conventional zones to `last_alloc`, requires raid-stripe-tree for data DUP, and activates zones if only one side is active.
- `btrfs_load_block_group_raid1()` tolerates missing devices only in degraded mode, normalizes conventional zones, verifies matching write pointers for non-degraded mounts, and requires raid-stripe-tree for data mirrored profiles.
- `btrfs_load_block_group_raid0()` reconstructs logical allocation from per-device stripe positions, verifies stripe ordering, forbids multiple partial stripes, checks row gaps, and requires raid-stripe-tree for data RAID0.
- `btrfs_load_block_group_raid10()` applies RAID0-style reconstruction to mirrored stripe groups and verifies mirrored write-pointer consistency.

Zone accounting and active-zone limits:
- `btrfs_dev_set_active_zone()` and `btrfs_dev_clear_active_zone()` maintain per-device active-zone bitmaps and `active_zones_left`.
- `btrfs_zone_activate()` activates all underlying device zones for a block group, honors reserved active zones for metadata/system needs, adds the block group to `zone_active_bgs`, and sets `BLOCK_GROUP_FLAG_ZONE_IS_ACTIVE`.
- `btrfs_can_activate_zone()` checks whether an allocation profile can obtain enough active zones and sets `BTRFS_FS_NEED_ZONE_FINISH` when not.
- `btrfs_check_active_zone_reservation()` reserves active-zone capacity for metadata, tree-log, and system block groups, then subtracts reservations already consumed by active metadata/system groups.
- `btrfs_zoned_activate_one_bg()` tries to activate an inactive metadata/system block group and can optionally finish another active data group to free active-zone budget.
- `btrfs_zone_finish_one_bg()` selects the active data block group with the least remaining capacity and finishes it.

Sequential allocation and unusable space:
- `btrfs_calc_zone_unusable()` computes unusable space as already-advanced write-pointer bytes beyond used bytes plus capacity lost at the tail of the block group.
- It marks the free-space cache finished and sets `free_space_ctl->free_space` to bytes from current allocation offset to zone capacity.

Data zone append and ordered extent repair:
- `btrfs_use_zone_append()` uses zone append only for zoned data writes to sequential-zone block groups, excluding reads, metadata, and data relocation.
- `btrfs_record_physical_zoned()` adjusts ordered checksum logical addresses after zone append reports the actual physical write location.
- `btrfs_finish_ordered_zoned()` rewrites or splits ordered extents when zone append caused non-contiguous physical results, and frees dummy checksum structures for nodatasum I/O.
- `btrfs_rewrite_logical_zoned()` updates the ordered extent and its extent map with the final logical disk bytenr.
- `btrfs_zoned_split_ordered()` splits both extent map and ordered extent around a contiguous zone-append result segment.

Metadata write-pointer enforcement:
- `btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written exactly at a block group’s `meta_write_pointer`.
- `check_bg_is_active()` activates tree-log/metadata/system groups as needed, pivots active metadata/system groups, waits for writeback before finishing old groups, and avoids deadlocks when unsent I/O exists.
- Return meanings are explicit: `0` means the metadata buffer may be written, `-EAGAIN` means a commit-time hole must be filled, and `-EBUSY` means callers should bail out.

Device replace support:
- `read_zone_info()` maps a logical address to read mirrors and reads zone state from a usable mirror, rejecting RAID56.
- `btrfs_sync_zone_write_pointer()` advances a target device’s sequential zone by zero-filling from the current target position to the source write pointer.

Zone finishing:
- `btrfs_zone_finish()` calls `do_zone_finish()` for a block group.
- `do_zone_finish()` verifies active state, avoids finishing metadata groups with unwritten allocated space, can set a block group read-only and wait for reservations/ordered extents/extent-buffer writeback, marks allocation as full, updates metadata write pointer and free space, clears tree-log/data-reloc special markers, finishes underlying device zones, removes the group from `zone_active_bgs`, and wakes waiters.
- `call_zone_finish()` issues `REQ_OP_ZONE_FINISH` for sequential zones, restores reserved active-zone counts for metadata/system, and clears device active-zone bits.
- `btrfs_zone_finish_endio()` finishes a block group after an endio reaches the last allocatable unit.
- `btrfs_schedule_zone_finish_bg()` queues asynchronous finishing for metadata block groups near the end, waiting on the last extent buffer first.

Zoned data relocation:
- `btrfs_zoned_reserve_data_reloc_bg()` chooses or allocates an empty data block group for zoned relocation, moves it into the data-relocation space info when needed, sets `fs_info->data_reloc_bg`, marks `BLOCK_GROUP_FLAG_ZONED_DATA_RELOC`, and activates it.
- `btrfs_clear_data_reloc_bg()` clears the global data relocation block-group marker.
- `btrfs_zoned_release_data_reloc_bg()` clears the relocation runtime flag after the last relocated range has been written.

Reclaim and reset:
- `btrfs_free_zone_cache()` drops per-device zone caches after mount-time use.
- `btrfs_zoned_should_reclaim()` compares total device bytes used against total filesystem bytes and the configured reclaim threshold.
- `btrfs_reset_unused_block_groups()` finds fully zone-unusable unused block groups of a given space type, resets all underlying zones, resets allocation offset/free space/accounting, and returns reclaimed bytes to the space info.

Statistics:
- `btrfs_show_zoned_stats()` prints active block-group count, reclaimable/unused counts, reclaim need, data relocation and tree-log block-group ids, and details for every active zone/block group.

Cross-file relationships:
- Uses `volumes.h` chunk maps, devices, stripe geometry, device replace state, and mapping APIs.
- Uses `block-group.h` and `space-info.h` for block-group runtime flags, allocation offsets, free-space accounting, and space-info lists.
- Uses `bio.h`, ordered extent code, compression-independent checksum state, and extent maps for zone append completion.
- Uses `disk-io.h` superblock helpers and extent-buffer writeback waiting.
- Uses `transaction.h` and chunk allocation to reserve data relocation block groups.
- Exposes declarations and inline helpers through `zoned.h`.

Important invariants and risks:
- Zoned filesystems require all devices to have the same zone size; regular devices are allowed only via conventional-zone emulation.
- Zone size must align to `BTRFS_STRIPE_LEN`.
- Mixed block groups, space cache v1, and NODATACOW are incompatible with zoned mode.
- Sequential block-group allocation is append-only: `alloc_offset`, `zone_capacity`, and `meta_write_pointer` must never imply writes behind a device write pointer.
- Data non-SINGLE zoned profiles require raid-stripe-tree support.
- RAID5/6 zoned block groups are not supported by this loader.
- Active-zone accounting must reserve capacity for metadata/system/tree-log needs before data activation.
- Metadata writes are serialized around `zoned_meta_io_lock` and must follow `meta_write_pointer` exactly.
- Zone append can change physical placement; ordered extents and checksum logical addresses must be repaired before completion.
- Zone finish must wait for relevant outstanding writes unless the caller proves the last allocatable block has completed.
- Resetting unused block groups assumes they are fully zone-unusable and unused; partial reset is intentionally avoided.
