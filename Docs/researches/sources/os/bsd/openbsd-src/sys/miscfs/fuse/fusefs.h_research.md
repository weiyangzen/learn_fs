# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs.h

Purpose: Defines FUSE mount state, sysctl identifiers, unsupported-operation flags, and kernel helper prototypes.

Key contents:
- Sysctl IDs and names for open FUSE devices, inbound request count, waiting request count, and pool pages.
- `struct fusefs_mnt` stores mount pointer, unsupported operation bitmap, max read size, session init state, `allow_other`, and backing device.
- `UNDEF_*` flags record daemon operations that returned `ENOSYS`, allowing later calls to skip optional or unsupported protocol operations.
- Declares `fusefs_vops`, `fusefs_fbuf_pool`, file helpers, device helpers, `FUSE_ROOTINO`, and `VFSTOFUSEFS()`.

Filesystem relevance:
- This is the shared internal contract among FUSE mount, vnode, device, file, lookup, and buffer code.
