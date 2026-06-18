# File Research: sources/os/bsd/openbsd-src/sys/sys/file.h

This header defines kernel file object types, file operations, and file reference helpers.

Key definitions:
- Descriptor object types: `DTYPE_VNODE`, `SOCKET`, `PIPE`, `KQUEUE`, `DMABUF`, `SYNC`.
- `struct fileops` with read/write/ioctl/kqfilter/stat/close/seek callbacks.
- `FO_POSITION`.
- `struct file` with global linkage, mutex, flags, internal flags, type, refcount, credentials, ops, offset, private data, and IO metrics.
- Internal flags: `FIF_HASLOCK`, `FIF_INSERTED`.
- Reference helpers: `FREF`, `FRELE`, `FDUP_MAX_COUNT`.

Kernel APIs/globals:
- `fdrop`
- `foffset`
- `LIST_HEAD(filelist, file)`
- `maxfiles`, `numfiles`, `socketops`, `vnops`

Risk notes:
- Some `fileops` may run without the kernel lock; implementers must honor per-file locking.
- `FREF` calls `vfs_stall_barrier()` before incrementing the refcount, coupling file reference acquisition with VFS stall coordination.
