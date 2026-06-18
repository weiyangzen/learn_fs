# File Research: sources/teaching/minix/minix/fs/ext2/table.c

This file defines the ext2 fsdriver dispatch table.

Registered operations:
- Mount/unmount, lookup, putnode.
- Read/write/peek via `fs_readwrite`.
- Getdents, truncate, seek.
- Create, mkdir, mknod, hard link, unlink/rmdir, rename.
- Symlink creation/readlink.
- Stat, chown, chmod, utime, mountpoint, statvfs, sync.
- LMFS driver, block read/write/peek/flush hooks.

Role:
- This is the binding layer between MINIX fsdriver requests and ext2 implementation functions.
- `_TABLE` causes global definitions rather than extern declarations through `glo.h`.
