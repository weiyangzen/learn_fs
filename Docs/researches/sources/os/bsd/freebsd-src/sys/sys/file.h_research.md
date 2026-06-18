# File Research: sources/os/bsd/freebsd-src/sys/sys/file.h

## Purpose
Defines kernel file object types, file operation vectors, the kernel `struct file`, reference helpers, and inline dispatch wrappers.

## Main Interfaces
- Descriptor types: `DTYPE_NONE`, `VNODE`, `SOCKET`, `PIPE`, `FIFO`, `KQUEUE`, `CRYPTO`, `MQUEUE`, `SHM`, `SEM`, `PTS`, `DEV`, `PROCDESC`, `EVENTFD`, `TIMERFD`, `INOTIFY`, `JAILDESC`, `NTSYNC`.
- File offset locking APIs and flags: `FOF_*`, `foffset_*`, `fsetfl_*`.
- Operation typedefs: read/write, truncate, ioctl, poll, kqfilter, stat, close, fdclose, chmod, chown, sendfile, seek, kinfo, mmap, aio, seals, fallocate, fspacectl, compare, fork.
- `struct fileops` and flags `DFLAG_PASSABLE`, `DFLAG_SEEKABLE`, `DFLAG_FORK`.
- `struct file`: flags, refcount, data pointer, ops, vnode, credentials, type, vnode-specific sequencing/advice/cdevpriv, offset.
- Userland/sysctl `struct xfile`.
- Kernel globals: `vnops`, `badfileops`, `path_fileops`, `socketops`, `maxfiles`, `maxfilesperproc`.
- Reference/get APIs: `fget*`, `fdrop`, `fdrop_close`, `fhold`, vnode-specific getters, remote getters.
- Initialization and vnode/file helpers: `finit`, `finit_vnode`, `vn_*`, invalid operation stubs.
- Inline operation dispatchers: `fo_read`, `fo_write`, `fo_truncate`, `fo_ioctl`, `fo_poll`, `fo_stat`, `fo_close`, `fo_kqfilter`, `fo_chmod`, `fo_chown`, `fo_sendfile`, `fo_seek`, `fo_fill_kinfo`, `fo_mmap`, `fo_aio_queue`, `fo_add_seals`, `fo_get_seals`, `fo_fallocate`, `fo_fspacectl`, `fo_cmp`.

## Dependencies And Integration
Kernel side includes locks, queues, refcounts, VM types, and forward declarations for vnode, proc, uio, knote, nameidata, credentials, and Capsicum rights. It is the central polymorphic object layer beneath descriptors and VFS/socket/device paths.

## Risk Notes
Reference release paths differ: `fdrop` treats last release as unlikely, while `fdrop_close` treats it as likely. Optional fileops return `ENODEV` or `EINVAL` depending on operation. `struct file` lock annotations matter for offset, vnode advice, and cdev private data.
