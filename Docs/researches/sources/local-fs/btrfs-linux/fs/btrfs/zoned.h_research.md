# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zoned.h

This header declares the zoned-mode interface, defines per-device zoned state, supplies non-zoned build stubs, and provides inline helpers for zone type checks, empty-zone bitmap updates, zoned metadata/data relocation locks, and full-block-group checks.

Main structure:
- `struct btrfs_zoned_device_info` stores per-device zone geometry and state:
  - `zone_size`, `zone_size_shift`, and `nr_zones`.
  - `max_active_zones`, `reserved_active_zones`, and atomic `active_zones_left`.
  - Bitmaps for sequential zones, empty zones, and active zones.
  - Optional `zone_cache` for reported zone data.
  - Cached superblock log zones for all superblock mirrors.

Exported zoned API when `CONFIG_BLK_DEV_ZONED` is enabled:
- Device setup/teardown: `btrfs_get_dev_zone_info_all_devices()`, `btrfs_get_dev_zone_info()`, `btrfs_destroy_dev_zone_info()`, `btrfs_clone_dev_zone_info()`.
- Mount validation: `btrfs_check_zoned_mode()`, `btrfs_check_mountopts_zoned()`.
- Superblock log locations: `btrfs_sb_log_location_bdev()`, `btrfs_sb_log_location()`, `btrfs_advance_sb_log()`, `btrfs_reset_sb_log_zones()`.
- Allocation/reset helpers: `btrfs_find_allocatable_zones()`, `btrfs_reset_device_zone()`, `btrfs_ensure_empty_zones()`.
- Block-group state: `btrfs_load_block_group_zone_info()`, `btrfs_calc_zone_unusable()`, `btrfs_zone_activate()`, `btrfs_zone_finish()`, `btrfs_can_activate_zone()`, `btrfs_zone_finish_endio()`, `btrfs_schedule_zone_finish_bg()`.
- I/O helpers: `btrfs_use_zone_append()`, `btrfs_record_physical_zoned()`, `btrfs_check_meta_write_pointer()`, `btrfs_zoned_issue_zeroout()`, `btrfs_sync_zone_write_pointer()`, `btrfs_finish_ordered_zoned()`.
- Relocation/reclaim/stats: `btrfs_clear_data_reloc_bg()`, `btrfs_zoned_reserve_data_reloc_bg()`, `btrfs_free_zone_cache()`, `btrfs_zoned_should_reclaim()`, `btrfs_zoned_release_data_reloc_bg()`, `btrfs_zone_finish_one_bg()`, `btrfs_zoned_activate_one_bg()`, `btrfs_check_active_zone_reservation()`, `btrfs_reset_unused_block_groups()`, `btrfs_show_zoned_stats()`.

Non-zoned build stubs:
- Most helpers become no-ops or regular-filesystem fallbacks.
- `btrfs_check_zoned_mode()` rejects zoned filesystems with `-EOPNOTSUPP` when zoned block-device support is not compiled.
- Superblock location helpers return regular Btrfs superblock offsets.
- Zone append is disabled.
- Zone reset/zeroout synchronization returns unsupported where meaningful.

Inline helpers:
- `btrfs_dev_is_sequential()` checks the sequential-zone bitmap for a physical position.
- `btrfs_dev_is_empty_zone()` treats devices without zone info as empty and otherwise checks the empty-zone bitmap.
- `btrfs_dev_set_empty_zone_bit()`, `btrfs_dev_set_zone_empty()`, and `btrfs_dev_clear_zone_empty()` update empty-zone state.
- `btrfs_check_device_zone_type()` enforces that zoned filesystems use either regular devices or zoned devices matching the filesystem zone size, while non-zoned filesystems reject zoned devices.
- `btrfs_check_super_location()` allows superblocks only on non-sequential zones for zoned devices.
- `btrfs_can_zone_reset()` requires sequential zones and zone-aligned physical/length.
- `btrfs_zoned_meta_io_lock()` and `btrfs_zoned_meta_io_unlock()` wrap `fs_info->zoned_meta_io_lock` only for zoned filesystems.
- `btrfs_clear_treelog_bg()` clears the global tree-log block-group marker under lock.
- `btrfs_zoned_data_reloc_lock()` and `btrfs_zoned_data_reloc_unlock()` serialize data relocation I/O only for zoned data-reloc roots.
- `btrfs_zoned_bg_is_full()` checks `alloc_offset == zone_capacity` and asserts zoned mode.

Cross-file relationships:
- Implemented by `zoned.c`.
- Consumed by mount/device setup, block-group allocation/reclaim, metadata writeback, ordered extent completion, scrub/repair paths, and device replace.
- Includes `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h` because zoned policy spans devices, chunks, block groups, metadata buffers, and inodes.

Important invariants:
- `zone_info` may be absent for non-zoned devices in non-zoned filesystems; helpers must tolerate that.
- Empty/active/sequential state is indexed by `pos >> zone_size_shift`.
- Superblock locations on true zoned devices must avoid sequential write-required zones except through the dedicated log-zone mechanism.
- Metadata I/O and data relocation locks are conditional on zoned mode and must not impose overhead or locking on regular filesystems.
- `btrfs_zoned_bg_is_full()` is valid only for zoned block groups.
