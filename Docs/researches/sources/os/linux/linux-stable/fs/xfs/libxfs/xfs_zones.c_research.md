# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.c

## Purpose

Validates block-layer zone descriptors for zoned realtime XFS.

## Main Function

- `xfs_validate_blk_zone`

This checks zone capacity, zone length, zone type, zone condition, and write pointer position against expected XFS realtime group geometry.

## Zone Handling

Sequential write required zones:
- Empty zones produce write pointer `0`.
- Open, closed, and active zones must have write pointers within `[start, start + capacity)`.
- Full zones produce write pointer equal to capacity.
- Offline, readonly, and non-write-pointer conditions are rejected.

Conventional zones:
- Only `BLK_ZONE_COND_NOT_WP` is accepted.

## Important Invariants

- Zone capacity in filesystem blocks must equal expected realtime group capacity.
- Zone length in filesystem blocks must equal expected raw zone size.
- All zones, including the last zone, must have uniform capacity.
- Sequential zone write pointers are converted from 512-byte block units to filesystem blocks.

## Dependencies

- Uses mount conversion macros for block units.
- Reports validation failures through XFS warnings.

## Research Notes

This file enforces the block-device assumptions behind zoned realtime groups. Uniform zone geometry is required because higher-level garbage collection and allocation logic assume it.
