# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_bmap.c

## Purpose
Maps cd9660 logical file blocks to device blocks for VFS/buffer-cache consumers.

## Main Elements
- Returns the underlying device buffer object when requested.
- Computes physical block number from `iso_start + logical block` shifted by filesystem block size.
- Calculates forward readahead run length capped by `MAXBSIZE`.
- Reports no backward run.

## Dependencies And Integration
Used by cd9660 vnode operations and buffer cache for ISO file extents.

## Risk Notes
Assumes cd9660 files are contiguous extents, matching ISO 9660 layout.
