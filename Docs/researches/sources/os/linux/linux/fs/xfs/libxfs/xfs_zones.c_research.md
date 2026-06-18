# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.c

## Purpose

`xfs_zones.c` validates block-layer zone descriptors against XFS zoned realtime geometry and extracts write pointer positions for sequential zones.

## Main Content

- Validates sequential write-required zones:
  - Empty zones set write pointer to zero.
  - Open, closed, and active zones require write pointer within zone capacity.
  - Full zones set write pointer to capacity.
  - Not-write-pointer, offline, and readonly conditions are rejected.
  - Unknown conditions are rejected.
- Validates conventional zones:
  - Only `BLK_ZONE_COND_NOT_WP` is accepted.
- Validates generic zone geometry:
  - Zone capacity must match expected RT group capacity.
  - Zone length must match expected raw zone size/geometry.
  - Dispatches by zone type to conventional or sequential validation.
  - Rejects unsupported zone types.

## Key Interfaces and Invariants

- All zones, including the last zone, must have uniform capacity matching the RT group size in the superblock.
- Sequential zone write pointers are converted from 512-byte sectors to filesystem blocks relative to zone start.
- A sequential zone write pointer must be at least zone start and strictly below start plus capacity unless the zone is full.
- Validation emits warnings with zone number and failed field values.

## Dependencies

Depends on Linux block zone definitions, XFS mount block conversion helpers, realtime group block types, and warning infrastructure.
