# File Research: sources/os/bsd/openbsd-src/sys/sys/fusebuf.h

This header defines OpenBSD kernel-to-userland FUSE request/response buffer structures.

Key definitions:
- `FUSEBUFMAXSIZE`.
- `struct fb_hdr` with queue linkage, data length, errno, operation type, inode, UUID, caller tid/uid/gid, and umask.
- `struct fb_io` for file operations with fd, inode, offset, length, mode, flags, and rdev.
- `struct fusebuf` with header, operation union (`statvfs`, `stat`, `fb_io`), and data pointer.
- Convenience field macros for header and union fields.
- `fbtod(fb,t)` data conversion macro.
- Setattr flags: `FUSE_FATTR_*`.
- Operation types: `FBT_LOOKUP`, `GETATTR`, `SETATTR`, `READLINK`, `SYMLINK`, `MKNOD`, `MKDIR`, `UNLINK`, `RMDIR`, `RENAME`, `LINK`, `OPEN`, `READ`, `WRITE`, `STATFS`, `RELEASE`, `FSYNC`, `FLUSH`, `INIT`, `OPENDIR`, `READDIR`, `RELEASEDIR`, `FSYNCDIR`, `ACCESS`, `DESTROY`, `RECLAIM`.

Kernel APIs:
- `fb_setup`
- `fb_queue`
- `fb_delete`

Risk notes:
- Requests are correlated by `fh_uuid`; userland replies must preserve it.
- Large read/write/readdir operations can be split across multiple fusebufs with changing offsets.
