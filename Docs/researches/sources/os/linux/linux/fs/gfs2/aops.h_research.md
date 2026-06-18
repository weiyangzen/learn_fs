# File Research: sources/os/linux/linux/fs/gfs2/aops.h

Declares GFS2 address-space helper functions shared outside `aops.c`.

Exports:
- `adjust_fs_space(struct inode *inode)`
- `gfs2_jdata_writeback(struct address_space *mapping, struct writeback_control *wbc)`

Integration:
- Used by resource-index grow/statfs paths and journaled-data writeback callers.
