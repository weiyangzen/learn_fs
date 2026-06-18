# File Research: sources/os/linux/linux-stable/fs/hfs/part_tbl.c

## Scope

Parses old and new Macintosh partition maps to locate an HFS partition inside a block device.

## APIs And Behavior

`hfs_part_find()` reads the partition map block at the current candidate start, distinguishes old and new partition map signatures, scans entries for either old `TFS1` IDs or new `Apple_HFS` partition types, honors the mount `part` option, and updates `part_start` and `part_size` on success.

## State And Dependencies

The function uses `sb_bread512()` for sector-sized reads regardless of filesystem block size and reads `HFS_SB(sb)->part` to select a specific partition index or the first matching partition.

## Risks And Invariants

The new partition map loop trusts `pmMapBlkCnt` as the number of map blocks to scan but stops if subsequent signatures are invalid. Old-map scanning does not break on match, so later matching entries can overwrite earlier matches unless a specific `part` was requested.
