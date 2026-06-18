# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/file.h

Defines the illumos kernel `file_t` open-file object and user/kernel file flag constants. `file_t` holds short-term lock, open flags, extra flags, vnode pointer, file offset, credentials, audit data, reference count, and OFD lock pointer. Comments specify `f_tlock` protects most fields while `f_rwlock` elsewhere protects vnode and credentials.

Defines standard and illumos-specific open flags: `FREAD`, `FWRITE`, `FNDELAY`, `FAPPEND`, `FSYNC`, `FNONBLOCK`, create/truncate/exclusive/noctty, large-file, xattr, nofollow, nolinks, ignorecase, xattr directory open, `FSEARCH`, `FEXEC`, `FCLOEXEC`, `FDIRECTORY`, `FDIRECT`, and `FCLOFORK`. Kernel-only fake ioctl/open flags include data-model bits, `FKIOCTL`, and `FKLYR`.

Also exposes historical `flock(3C)` constants and kernel file-descriptor APIs such as `getf`, `releasef`, `closef`, `ufalloc`, `falloc`, `setf`, fd flag accessors, `close_exec`, poll-info helpers, socket async query, and zone-change checking.
