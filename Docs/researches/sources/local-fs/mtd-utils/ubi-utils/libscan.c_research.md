# File Research: sources/local-fs/mtd-utils/ubi-utils/libscan.c

## Role
MTD scan library for identifying UBI erase-counter headers and eraseblock status.

## Main Behavior
- Allocates `ubi_scan_info` and one EC/status entry per eraseblock.
- For each eraseblock:
  - checks bad-block status,
  - reads the UBI EC header,
  - classifies empty/non-UBI/corrupted/valid blocks,
  - validates EC header magic, CRC, erase counter limit, VID offset, and data offset consistency.
- Computes mean erase counter over valid EC headers.
- Records good/bad/empty/corrupted/alien counts.

## Interfaces And Dependencies
- Uses `libmtd` functions `mtd_is_bad` and `mtd_read`.
- Uses UBI media structs, endian conversion, and `mtd_crc32`.
- Uses `common.h` logging helpers.

## Notes
- Verbose mode 1 prints progress; verbose mode 2 prints per-block classification.
- Treats inconsistent offsets as corrupted eraseblocks rather than fatal scan errors.
