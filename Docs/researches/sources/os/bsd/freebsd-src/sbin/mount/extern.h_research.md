# File Research: sources/os/bsd/freebsd-src/sbin/mount/extern.h

## Summary
Shared declarations for the generic `mount` utility.

## Main Contents
- Declares `checkvfsname()` and `makevfslist()` from `vfslist.c`.
- Declares `mount_fs()` from `mount_fs.c`.

## Dependencies And Integration
Included by `mount.c`, `mount_fs.c`, and `vfslist.c` to connect VFS list filtering and direct `nmount` mounting.
