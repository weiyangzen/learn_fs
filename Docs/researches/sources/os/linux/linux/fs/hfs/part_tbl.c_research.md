# File Research: sources/os/linux/linux/fs/hfs/part_tbl.c

Purpose: Parses old and new Macintosh partition maps to find the selected HFS partition start and size.

Key functions:
- `hfs_part_find()` reads the partition map block, detects old or new signatures, scans entries, and updates `part_start`/`part_size` when a matching HFS partition is found.

Dependencies and integration:
- Uses `sb_bread512()` from `hfs_fs.h`.
- Called by `hfs_mdb_get()` when the raw MDB is not found at the current start sector.
- Honors `HFS_SB(sb)->part` when the user selected a partition number.

Risk notes:
- Old-style support scans a fixed 42-entry table and matches `TFS1`.
- New-style support follows contiguous map blocks and matches `Apple_HFS`.
