# File Research: sources/teaching/minix/minix/fs/mfs/time.c

`time.c` implements `fs_utime`, the timestamp-setting operation. It opens the target inode, resets pending timestamp flags to ctime-only, then handles `atime` and `mtime` separately.

For each supplied `timespec`, `UTIME_NOW` sets the corresponding lazy update bit, `UTIME_OMIT` leaves the field unchanged, and explicit timestamps are stored directly using seconds only. MFS does not support subsecond timestamp resolution, so nanoseconds are discarded. The inode is marked dirty and released.
