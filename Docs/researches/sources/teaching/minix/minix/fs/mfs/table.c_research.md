# File Research: sources/teaching/minix/minix/fs/mfs/table.c

`table.c` defines `_TABLE` so global variables declared through `EXTERN` become definitions, includes the MFS headers, and instantiates the `mfs_table` fsdriver dispatch table.

The table maps VFS/fsdriver operations to MFS implementations: mount, unmount, lookup, putnode, read, write, peek, getdents, truncation, seek, create, mkdir, mknod, link, unlink, rmdir, rename, symlink creation/readlink, stat, chown, chmod, utime, mountpoint marking, statvfs, and sync. It also exposes libminixfs block-device operations for driver, bread/bwrite/bpeek, and bflush.
