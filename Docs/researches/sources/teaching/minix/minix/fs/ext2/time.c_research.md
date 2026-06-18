# File Research: sources/teaching/minix/minix/fs/ext2/time.c

This file implements explicit timestamp updates.

Entry point:
- `fs_utime(ino_nr, atime, mtime)`: applies `UTIME_NOW`, `UTIME_OMIT`, or explicit seconds values for atime and mtime, marks ctime for update, and dirties inode.

Important behavior:
- Clears stale atime/mtime update flags by assigning `rip->i_update = CTIME`.
- Ext2 subsecond timestamps are unsupported, so explicit times use `tv_sec` only.
- Final timestamp writes happen later through `update_times()`/`rw_inode()`.
