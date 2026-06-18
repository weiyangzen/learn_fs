# File Research: sources/os/linux/linux-stable/fs/gfs2/aops.h

## Purpose
Declares GFS2 address-space helper functions shared with other modules.

## Key Interfaces
- `adjust_fs_space()` updates statfs after grow/rindex changes.
- `gfs2_jdata_writeback()` writes journaled-data mappings.

## Dependencies
Includes `incore.h` for GFS2 inode/superblock types.
