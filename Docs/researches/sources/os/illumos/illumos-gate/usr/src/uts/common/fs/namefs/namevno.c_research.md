# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevno.c

Implements NAMEFS vnode operations for mounted file descriptors. NAMEFS is mostly a forwarding layer from the mounted namenode vnode to the underlying file descriptor vnode, with special handling for open-time vnode switching and for attributes/permissions stored on the namenode itself.

Key elements:
- `nm_open()` holds the underlying `nm_filevp`, calls `VOP_OPEN()`, and handles filesystems that switch the opened vnode. If the underlying vnode changes, it finds or creates a new `namenode` keyed by `(outfilevp, mountpt)`, initializes a NAMEFS vnode for it, inserts it in the namenode hash, and returns that vnode.
- `nm_close()` clears process locks/shares on the NAMEFS vnode, forwards `VOP_CLOSE()` to `nm_filevp`, fsyncs on the last close, removes transient `NMNMNT` entries from the namefs hash, and releases the underlying file vnode hold.
- Simple pass-through operations: `nm_read()`, `nm_write()`, `nm_ioctl()`, `nm_fsync()`, `nm_fid()`, `nm_rwlock()`, `nm_rwunlock()`, `nm_seek()`, `nm_realvp()`, and `nm_poll()`.
- `nm_getattr()` returns stored namenode attributes, but refreshes `AT_SIZE` from the underlying vnode.
- `nm_setattr()` updates only mutable stored namenode attributes, rejects `AT_NOSET` and `AT_SIZE`, uses `secpolicy_vnode_setattr()`, strips sticky bit on mode set, updates uid/gid/time fields, and serializes via the underlying vnode write lock plus `nm_lock`.
- `nm_access()` first checks permissions against NAMEFS-stored mode/uid/gid through `nm_access_unlocked()`, then checks the underlying vnode with `VOP_ACCESS()`.
- `nm_create()` supports the empty-name open/create case on a mounted file descriptor mount point; non-exclusive create returns the mount vnode if access passes, exclusive create returns `EEXIST`.
- `nm_link()` rejects links to mounted file descriptors with `EXDEV`.
- `nm_inactive()` releases the vnode reference, closes the stored file pointer for non-`NMNMNT` nodes, invalidates/frees the vnode, drops non-namefs VFS references, frees allocated node ids, and frees the namenode.
- `nm_vnodeops_template` registers NAMEFS VOPs and explicitly errors unsupported dispose.

Dependencies:
- NAMEFS internals from `sys/fs/namenode.h`: `VTONM`, `NMTOV`, `namefind`, `nameinsert`, `nameremove`, `namenodeno_alloc/free`, `ntable_lock`, `namevfs`.
- illumos vnode/VFS APIs: `VOP_OPEN`, `VOP_CLOSE`, `VOP_GETATTR`, `VOP_SETATTR`, `VOP_ACCESS`, `VOP_FSYNC`, `VOP_REALVP`, vnode holds/releases, `vn_alloc`, `vn_setops`, `vn_exists`, `vn_invalid`, `vn_free`.
- File/lock/security helpers: `cleanlocks`, `cleanshares`, `closef`, `secpolicy_vnode_access2`, `secpolicy_vnode_setattr`, `groupmember`.

Research notes:
- The main correctness path is `nm_open()` vnode substitution. It preserves NAMEFS identity by replacing the caller’s vnode with an existing or newly-created namenode for the switched underlying vnode.
- Attributes intentionally split between NAMEFS metadata and underlying vnode size; mode/owner/time changes affect the mounted descriptor node, not the target file object itself.
- `nm_inactive()` depends on `NMNMNT` to distinguish nodes that hold only a vnode reference from nodes whose `nm_filep` must be closed.
