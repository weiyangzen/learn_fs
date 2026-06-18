# File Research: sources/os/linux/linux-stable/fs/udf/lowlevel.c

## Summary
Provides low-level optical-media helper routines for determining multisession start and last written block.

## Key Functions
- `udf_get_last_session()`: queries the CD-ROM layer for multisession information and returns the XA session start LBA when available.
- `udf_get_last_block()`: queries the CD-ROM layer for the last written block, falling back to block-device size.

## Important Behavior
Both helpers use `disk_to_cdi()` to detect CD-ROM support. If CD-ROM multisession or last-written queries fail, the code falls back conservatively: session start is zero, and last block is derived from `sb_bdev_nr_blocks()` when it fits in `udf_pblk_t`.

## Risks
These helpers bridge generic block devices and optical-specific CD-ROM APIs. Bogus or unavailable CD-ROM responses are expected, so fallback behavior is part of normal mounting robustness.
