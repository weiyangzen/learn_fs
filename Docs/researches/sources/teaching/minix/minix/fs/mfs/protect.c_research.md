# File Research: sources/teaching/minix/minix/fs/mfs/protect.c

`protect.c` implements metadata permission/ownership changes. `fs_chmod` opens the inode, rejects read-only filesystems, replaces only the permission bits (`ALL_MODES`) while preserving file type and other mode bits, marks ctime for update, dirties the inode, returns the full resulting mode, and releases the inode.

`fs_chown` opens the inode, sets uid and gid, clears setuid/setgid bits, marks ctime, dirties the inode, returns the resulting mode, and releases the inode. Unlike `fs_chmod`, it does not explicitly check `s_rd_only`; dirtying on read-only filesystems would be caught by the inode dirty macro diagnostics.
