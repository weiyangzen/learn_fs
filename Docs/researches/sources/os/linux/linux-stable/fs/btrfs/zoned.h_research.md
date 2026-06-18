# File Research: sources/os/linux/linux-stable/fs/btrfs/zoned.h

## Purpose

`zoned.h` declares the Btrfs zoned-mode API and provides no-op fallbacks when `CONFIG_BLK_DEV_ZONED` is disabled. It also defines the per-device zoned metadata structure and lightweight helpers used throughout Btrfs.

## Main Structure

- `struct btrfs_zoned_device_info`
  - `zone_size` and `zone_size_shift`
  - `nr_zones`
  - `max_active_zones`
  - `reserved_active_zones`
  - `active_zones_left`
  - bitmaps for sequential, empty, and active zones
  - optional `zone_cache`
  - cached superblock log zones

## Exported Zoned APIs

When zoned block support is enabled, the header declares functions for:

- device zone info load/clone/destroy
- zoned mode and mount option checks
- superblock log location, advancement, and reset
- allocatable-zone search
- zone reset and empty-zone validation
- block-group zone info loading and unusable-space calculation
- zone append decision and physical-position recording
- metadata write-pointer validation
- zeroout and dev-replace write-pointer synchronization
- active-zone activation/finish/accounting
- data relocation block-group reservation/release
- zone cache freeing
- reclaim decisions
- unused block-group reset
- zoned stats display

## Disabled-Config Behavior

When `CONFIG_BLK_DEV_ZONED` is disabled:

- Most APIs become no-ops or return regular filesystem behavior.
- `btrfs_check_zoned_mode()` rejects a filesystem that is actually marked zoned with `-EOPNOTSUPP`.
- Zone append is disabled.
- zone reset/zeroout/sync helpers return unsupported where appropriate.
- activation/finish helpers act as if all block groups are active and finishable.

## Inline Helpers

- `btrfs_dev_is_sequential()` checks if a device position is in a sequential zone.
- `btrfs_dev_is_empty_zone()` checks the empty-zone bitmap, treating non-zoned devices as empty.
- `btrfs_dev_set_empty_zone_bit()`, `btrfs_dev_set_zone_empty()`, and `btrfs_dev_clear_zone_empty()` update empty-zone state.
- `btrfs_check_device_zone_type()` allows regular devices in zoned filesystems via emulation, but rejects host-managed zoned devices for non-zoned filesystems.
- `btrfs_check_super_location()` ensures superblocks on zoned devices are not placed in sequential-write-required zones.
- `btrfs_can_zone_reset()` validates sequential-zone and alignment requirements for resets.
- `btrfs_zoned_meta_io_lock()` and unlock gate metadata IO serialization only in zoned mode.
- `btrfs_clear_treelog_bg()` clears the tracked tree-log block group.
- `btrfs_zoned_data_reloc_lock()` and unlock serialize zoned data relocation IO.
- `btrfs_zoned_bg_is_full()` checks whether allocation reached zone capacity.

## Dependencies

The header depends on Linux block/zoned block definitions, atomics, spinlocks, mutexes, seq_file, and Btrfs local headers for messages, volumes, disk IO, block groups, and inode helpers.

## Research Notes

This header is the compatibility boundary for zoned support. It lets most call sites use zoned helpers unconditionally while preserving clean behavior in kernels built without zoned block support.
