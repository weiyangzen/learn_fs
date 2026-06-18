# File Research: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.h

`mount_tmpfs.h` declares `mount_tmpfs()` and `mount_tmpfs_parseargs()` for the tmpfs mount helper.

The parse function exposes argument parsing into `struct tmpfs_args`, mount flags, and canonical device/directory buffers. This is more modular than most other mount helpers in the group.
