# File Research: sources/teaching/minix/minix/fs/mfs/proto.h

`proto.h` declares the internal MFS function surface and maps `put_block` directly to `lmfs_put_block`. It forward-declares common structs and groups prototypes by implementation file.

The declared API covers zone/cache operations, inode allocation/reference/disk I/O, link/unlink/rename/truncation, sync, mount/unmount/mountpoint handling, file/directory/symlink creation, lookup and directory search, chmod/chown, read/write/getdents/block mapping, stat/statvfs, bitmap accounting, timestamp updates, byte-order conversion, and write-side block allocation/mapping.

This file is included through `fs.h`, so it is the main cross-module contract for MFS.
