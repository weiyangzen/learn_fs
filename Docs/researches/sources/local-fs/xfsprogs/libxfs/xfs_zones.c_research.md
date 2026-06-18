# File Research: sources/local-fs/xfsprogs/libxfs/xfs_zones.c

This file validates block-device zone descriptions for zoned XFS realtime devices.

`xfs_validate_blk_zone_seq` handles sequential-write-required zones. Empty zones report write pointer 0. Open, closed, and active zones require the device write pointer to lie within `[zone->start, zone->start + capacity)`, then translate it to filesystem blocks relative to the zone start. Full zones report write pointer equal to capacity. Non-write-pointer, offline, readonly, and unknown conditions are rejected with warnings.

`xfs_validate_blk_zone_conv` validates conventional zones; they must have `BLK_ZONE_COND_NOT_WP`. Any other condition is rejected.

`xfs_validate_blk_zone` first checks uniform zone capacity against the expected rtgroup capacity and zone length against expected raw group size. This matters because zoned realtime garbage collection assumes equal-size zones. It then dispatches by zone type: conventional or sequential-write-required. Unsupported zone types are rejected. The output `write_pointer` is meaningful for sequential zones and is expressed as an rtgroup-relative filesystem block number.
