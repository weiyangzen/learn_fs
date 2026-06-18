# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.h

## Purpose

`xfs_zones.h` defines zoned realtime allocator reservation constants and declares zone descriptor validation.

## Main Content

- Defines garbage collection zone reserve:
  - Three zones are reserved to guarantee GC forward progress with simpler accounting.
- Defines total reserved and minimum zone counts:
  - GC zones plus one write-reserve zone.
  - Minimum zones require one additional usable zone.
- Defines open-zone reserve:
  - One zone kept out of the general open pool for GC.
  - Minimum open zones count.
- Defines default max open zones as 128 for devices without an explicit limit or regular devices using the zoned allocator.
- Declares `xfs_validate_blk_zone`.

## Key Interfaces and Invariants

- Zoned allocation assumes enough reserved zones to relocate nearly full zones and continue user writes.
- `XFS_MIN_ZONES` and `XFS_MIN_OPEN_ZONES` encode allocator progress requirements, not merely hardware limits.

## Dependencies

Forward-declares realtime group and Linux block zone types; validation requires XFS mount and RT group block scalar types from surrounding headers.
