# File Research: sources/os/linux/linux/fs/hfsplus/part_tbl.c

## Role

Parses legacy and new-style Macintosh partition maps to locate an HFS/HFS+ partition within a block device.

## On-Disk Structures and Constants

- Block offsets:
  - `HFS_DD_BLK`: driver descriptor block.
  - `HFS_PMAP_BLK`: first partition map block.
  - `HFS_MDB_BLK`: HFS MDB block within a partition.
- Magic values:
  - `HFS_DRVR_DESC_MAGIC` (`"ER"`), `HFS_OLD_PMAP_MAGIC` (`"TS"`), `HFS_NEW_PMAP_MAGIC` (`"PM"`), HFS MDB (`"BD"`), and MFS MDB.
- `struct new_pmap`: packed new-style partition map entry with signature, map count, physical start/count, partition name, and partition type.
- `struct old_pmap`: packed old-style partition map with a signature and 42 entries containing start, size, and filesystem ID.

## Key Functions

- `hfs_parse_old_pmap()`
  - Scans 42 old-map entries.
  - Accepts entries with nonzero start/size, filesystem ID `"TFS1"`, and matching `sbi->part` if a specific partition was requested.
  - Adds the partition start to the caller-provided base and writes the partition size.
  - Returns `-ENOENT` when no matching partition exists.
- `hfs_parse_new_pmap()`
  - Uses `pmMapBlkCnt` as the map size.
  - Scans contiguous 512-byte map entries looking for `pmPartType == "Apple_HFS"` and optional matching partition index.
  - Reads additional map sectors through `hfsplus_submit_bio()` when the scan steps beyond the current minimum-I/O buffer.
  - Returns `-ENOENT` if no matching HFS partition is found or the signature chain stops.
- `hfs_part_find()`
  - Allocates a `hfsplus_min_io_size()` buffer.
  - Reads the first partition-map block at `*part_start + HFS_PMAP_BLK`.
  - Dispatches to old or new map parsing by 16-bit signature.
  - Frees the buffer and returns parser status.

## Dependencies

Uses `kmalloc/kfree`, HFS+ wrapper bio reads, endian helpers, minimum I/O sizing from `hfsplus_fs.h`, and `sbi->part` selection.

## Research Notes

The parser mutates `*part_start` by adding the selected partition’s physical start. Callers must pass a base sector and expect in-place update to the selected HFS/HFS+ partition. The code recognizes HFS partitions by legacy Mac partition maps rather than Linux partition infrastructure.
