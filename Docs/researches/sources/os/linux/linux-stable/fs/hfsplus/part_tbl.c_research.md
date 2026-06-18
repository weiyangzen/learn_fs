# File Research: sources/os/linux/linux-stable/fs/hfsplus/part_tbl.c

## Role

Parses classic Mac partition maps to locate an HFS/HFS+ partition start and size.

## On-Disk Structures

- `struct new_pmap`: Apple Partition Map entry with signature, map block count, physical partition start/count, partition name, and partition type.
- `struct old_pmap`: old partition map with signature and up to 42 entries containing start, size, and filesystem ID.

## Constants

- Block offsets:
  - driver descriptor block 0
  - first partition map block 1
  - MDB block 2
- Magic values:
  - driver descriptor `"ER"`
  - old partition map `"TS"`
  - new partition map `"PM"`
  - HFS MDB `"BD"`
  - MFS MDB

## Key Functions

- `hfs_parse_old_pmap()`
  - Scans 42 old map entries.
  - Selects entries with nonzero start/size and FSID `"TFS1"`.
  - Honors requested `sbi->part` if set.
  - Adds the selected entry start to `*part_start` and stores entry size in `*part_size`.
- `hfs_parse_new_pmap()`
  - Uses `pmMapBlkCnt` to walk Apple Partition Map entries.
  - Selects partition type `"Apple_HFS"`.
  - Honors requested `sbi->part`.
  - Advances through entries in the current I/O buffer, submitting additional reads when it crosses `hfsplus_min_io_size(sb)`.
  - Returns `-ENOENT` if no matching entry exists.
- `hfs_part_find()`
  - Allocates a minimum-I/O-size buffer.
  - Reads block `*part_start + HFS_PMAP_BLK`.
  - Dispatches by first 16-bit signature to old or new parser.
  - Frees the buffer and returns parser status.

## Dependencies

Uses `hfsplus_submit_bio()` for raw block reads, `hfsplus_min_io_size()` for safe buffer sizing, and mount option `sbi->part` as the partition selector.

## Research Notes

This parser mutates the caller’s `part_start` by adding the selected partition’s physical start. It treats partition map entries as 512-byte sectors even when the read buffer is larger. New-style maps are limited by the map block count, while old-style maps are fixed at 42 entries.
