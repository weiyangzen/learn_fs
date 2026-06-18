# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.h

This header declares the shared internal FUSE helper API and defines small compatibility-style wrappers around FreeBSD VFS and UIO structures.

Key contents:
- Externs for lookup-cache counters.
- Inline VFS/vnode helpers:
  - `vfs_isrdonly`
  - `vnode_mount`
  - `vnode_vtype`
  - `vnode_isvroot`
  - `vnode_isreg`
  - `vnode_isdir`
  - `vnode_islnk`
  - `uio_resid`
  - `uio_offset`
  - `uio_setoffset`
- Inline FUSE helpers:
  - `fuse_isdeadfs` tests `FSESS_DEAD`.
  - `fuse_iosize` returns the mount I/O size.
  - `fuse_validity_2_bintime` converts attr TTLs into monotonic `bintime`.
  - `fuse_validity_2_timespec` converts entry TTLs into `timespec` for namecache insertion.
  - `fuse_match_cred` checks daemon/user credential identity across real, saved, and effective uid/gid fields.
- Declares the main helper surface implemented by `fuse_internal.c`:
  - cached vnode lookup
  - access checks
  - attr caching
  - fsync callbacks
  - getattr
  - invalidation notifications
  - mknod
  - readdir and readdir data conversion
  - remove and rename
  - vnode disappearance
  - setattr
  - SUID/SGID clearing on write
  - new-entry request creation/core handling
  - forget callbacks and sends
  - init callback and init send
  - module init/destroy hooks
- Defines `struct pseudo_dirent`, a minimal layout used only for computing native directory record length from a FUSE name length.
- Defines `fuse_internal_checkentry`, validating that a returned `fuse_entry_out` has the expected vnode type and does not use null or root node ids for a new child.

Integration points:
- Includes `fuse_ipc.h` for dispatcher/ticket types and FUSE session flags.
- Includes `fuse_node.h` for vnode state, node ids, and attr-cache locking.
- Supplies the prototypes used by vnode ops, VFS ops, I/O, and file-handle code.

Notable risks and research hooks:
- TTL conversion saturates at `INT_MAX`; very long daemon TTLs effectively become persistent until that bound.
- `fuse_match_cred` is strict: all uid and gid variants must match.
- `fuse_internal_checkentry` rejects root id for new entries, so any daemon returning root as a child is treated as invalid.
