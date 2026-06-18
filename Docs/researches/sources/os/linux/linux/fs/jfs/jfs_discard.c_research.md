# File Research: sources/os/linux/linux/fs/jfs/jfs_discard.c

## Purpose
Implements JFS discard/TRIM support for online discard and the `FITRIM` ioctl path.

## Key Functions
- `jfs_issue_discard()` calls `sb_issue_discard()` for a filesystem block range using `GFP_NOFS`, logs failures with `jfs_err()`, and logs calls at info level.
- `jfs_ioc_trim()` converts user byte range fields to filesystem blocks, validates map state and range bounds, clamps end to map size, identifies allocation groups touched by the range, calls `dbDiscardAG()` for each AG, and updates `range->len` to the number of bytes actually trimmed.

## Error Handling
- Returns `-EINVAL` if the bmap is absent, `minlen` exceeds AG size, start is beyond map size, or range length is smaller than a filesystem block.
- `jfs_issue_discard()` does not propagate discard errors; it only logs them.

## Dependencies
- Uses `JFS_SBI(ip->i_sb)->bmap`, `ipbmap`, `BLKTOAG()`, and `dbDiscardAG()` from `jfs_dmap`.
- Called by `ioctl.c` for FITRIM and by `jfs_dmap.c` for mounted online discard.
