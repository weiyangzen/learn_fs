# File Research: sources/local-fs/kdave-linux/fs/btrfs/zoned.h

## Role

`zoned.h` declares Btrfs zoned-mode data structures, public zoned APIs, and inline fallbacks for kernels built without `CONFIG_BLK_DEV_ZONED`.

## Main Structure

`struct btrfs_zoned_device_info` stores per-device zoned metadata:

- zone size and shift
- number of zones
- maximum active zones
- reserved active zones
- atomic active-zones-left counter
- bitmaps for sequential, empty, and active zones
- optional zone cache
- cached superblock log zone descriptors

## Public Zoned API

When `CONFIG_BLK_DEV_ZONED` is enabled, the header declares APIs for:

- device zone info loading/destruction/cloning
- zoned mount validation and mount option validation
- superblock log location, advancement, and reset
- allocatable zone search and empty-zone enforcement
- block group zone info loading and unusable-space calculation
- zone append decisions and physical recording
- metadata write-pointer validation
- zeroout and dev-replace write-pointer sync
- zone activation, finish, and finish scheduling
- data relocation block group reservation/release
- zone cache freeing, reclaim decisions, active-zone reservation checks
- unused block group zone reset
- zoned stats display

It also exposes a test-only helper for loading block groups by RAID type.

## Non-Zoned Build Fallbacks

When `CONFIG_BLK_DEV_ZONED` is disabled, most functions become no-op or regular-device fallbacks. If a mounted filesystem is actually zoned, `btrfs_check_zoned_mode()` returns `-EOPNOTSUPP`. Zone append is disabled, zone activation always succeeds, and superblock locations use normal Btrfs offsets.

## Inline Helpers

The header provides small helpers to:

- Test whether a device position is sequential or empty.
- Set/clear empty-zone bits.
- Validate device zone type compatibility with filesystem zoned mode.
- Reject superblock locations inside sequential zones.
- Check whether a zone reset is aligned and valid.
- Lock/unlock zoned metadata I/O only in zoned mode.
- Clear tree-log block group tracking.
- Serialize zoned data relocation writes.
- Test whether a zoned block group is full.

## Relationship

`zoned.c` implements the enabled-mode functions declared here. Other Btrfs subsystems use this header to make zoned decisions while compiling cleanly on non-zoned configurations.
