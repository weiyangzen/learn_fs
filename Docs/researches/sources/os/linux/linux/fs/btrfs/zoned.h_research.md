# File Research: sources/os/linux/linux/fs/btrfs/zoned.h

## Purpose
Declares the public Btrfs zoned-mode API, `struct btrfs_zoned_device_info`, compile-time stubs for kernels without `CONFIG_BLK_DEV_ZONED`, and inline helpers for zone type/emptiness checks, active write locks, tree-log/data-relocation tracking, and full-block-group detection.

## Main Type
`struct btrfs_zoned_device_info` stores per-device zone metadata:
- `zone_size`, `zone_size_shift`, `nr_zones`
- active-zone limit and reserved active-zone count
- `active_zones_left`
- bitmaps for sequential zones, empty zones, and active zones
- optional cached zone reports
- cached superblock log-zone information for all mirrors

## Exported Zoned APIs
When `CONFIG_BLK_DEV_ZONED` is enabled, the header exports APIs for:
- Device zone-info discovery/destruction/cloning.
- Zoned-mode and mount-option validation.
- Superblock log location, advancement, and reset.
- Allocatable-zone search and empty-zone enforcement.
- Block-group zone-info loading and unusable-space accounting.
- Zone append selection and physical-location recording.
- Metadata write pointer checking.
- Zone zeroout, write-pointer sync for device replace, zone activation/finish.
- Active-zone reservation, reclaim, data relocation, unused block-group reset.
- Zoned statistics display.

A sanity-test-only hook exposes profile-specific block-group loading.

## Non-Zoned Build Stubs
Without `CONFIG_BLK_DEV_ZONED`, most functions become no-ops or conservative failures:
- Zoned mode check returns `-EOPNOTSUPP` if a zoned filesystem is detected.
- Zone append is disabled.
- Zone zeroout/write-pointer sync return `-EOPNOTSUPP`.
- Activation/finish are treated as successful no-ops.
- Reclaim/reset/stats helpers return neutral values.

## Inline Helpers
- `btrfs_dev_is_sequential()` tests whether a physical position is in a sequential zone.
- `btrfs_dev_is_empty_zone()` tests empty-zone bitmap state, treating non-zoned devices as empty.
- `btrfs_dev_set_zone_empty()` / `btrfs_dev_clear_zone_empty()` mutate empty-zone bitmap state.
- `btrfs_check_device_zone_type()` enforces device compatibility with zoned/non-zoned filesystems.
- `btrfs_check_super_location()` rejects superblocks in sequential zones unless the device is non-zoned.
- `btrfs_can_zone_reset()` checks sequential-zone and alignment requirements.
- `btrfs_zoned_meta_io_lock()` / `unlock()` serialize metadata I/O only in zoned mode.
- `btrfs_clear_treelog_bg()` clears the tracked tree-log block group if it matches.
- `btrfs_zoned_data_reloc_lock()` / `unlock()` serialize data relocation writes in zoned mode.
- `btrfs_zoned_bg_is_full()` tests `alloc_offset == zone_capacity`.

## Integration
This header depends on `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h`, reflecting how zoned mode cuts across device geometry, block-group allocation, metadata writeback, and data relocation.
