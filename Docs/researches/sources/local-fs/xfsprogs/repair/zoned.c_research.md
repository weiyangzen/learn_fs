# File Research: sources/local-fs/xfsprogs/repair/zoned.c

Validates zoned realtime devices against XFS rtgroup expectations.

Core flow:
- `check_zones` checks whether the realtime device is a block device and zoned via `BLKGETSIZE64` and `BLKGETZONESZ`.
- It verifies the device has enough zones for `sb_rgcount`.
- It reports zones in batches via `xfrog_report_zones`.
- For each zone, it checks consistent length, supported zone type, consistent capacity, and then calls `report_zones_cb`.
- `report_zones_cb` maps zone start sectors to realtime blocks/rtgroup, verifies the zone starts at rtgroup block zero, loads the rtgroup, warns if no rmap inode exists, and otherwise calls `libxfs_validate_blk_zone`.

Important behavior:
- Sequential-write-preferred and unknown zone types are fatal.
- Zone capacity must be consistent and not exceed zone size.
- Rtgroup rmap inode presence is important for full zone validation.
