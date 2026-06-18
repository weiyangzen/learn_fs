# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vnops.c

This file implements vnode operations for devfs. Directories are handled by devfs itself, while leaf VCHR/VBLK devices are normally substituted with specfs vnodes by `dv_find`; devfs then mainly sees forwarded operations for special-file metadata.

Core responsibilities:
- Defines `dv_vnodeops_template`, the vnode operation table used by devfs.
- Implements directory open/close/read/write/ioctl behavior.
- Implements attribute, permission, ACL, lookup, create, readdir, inactive, fid, locking, seek, and pathconf operations.
- Manages the distinction between memory attributes and persistent shadow attributes.
- Restricts real-console device permissions/access.

Important operations:
- `devfs_open` and `devfs_close` are directory-only; close clears locks and shares.
- `devfs_read`, `devfs_write`, and `devfs_ioctl` reject directory data I/O.
- `devfs_getattr` reads from `dv_attr` if present or from `dv_attrvp` otherwise, then merges devfs identity fields. It also forces the real console device to root-owned `0600`-style access.
- `devfs_setattr_dir` updates directory attributes either in memory or in the backing attribute store, with read-only fallback to memory attributes.
- `devfs_setattr` handles VDIR/VCHR/VBLK attribute changes, rejects unsupported `AT_NOSET`, ignores non-persistent fields, honors `DV_NO_FSPERM`, compares requested leaf permissions against default `minor_perm` or private defaults, removes shadow nodes when attributes return to defaults, and creates shadow nodes when non-default permissions need persistence.
- `devfs_pathconf` forwards `_PC_ACL_ENABLED` to the root attribute vnode.
- `devfs_getsecattr` fabricates ACLs if no attribute vnode exists; otherwise it forwards to the backing attribute vnode.
- `devfs_setsecattr` creates a backing attribute vnode if needed, forwards ACL changes under the backing vnode RW lock, and records `DV_ACL` for non-trivial ACLs.
- `devfs_unlocked_access` supports secpolicy checks while `dv_contents` is already held.
- `devfs_access` restricts console access via `secpolicy_console`, then checks either memory attributes or backing vnode access.
- `devfs_lookup` delegates to `dv_find`.
- `devfs_create` supports open-existing semantics only: absent entries become `EROFS`, exclusive create becomes `EEXIST`, writable directory create becomes `EISDIR`.
- `devfs_readdir` rebuilds directory contents when `DV_BUILD` is set, emits `.`, `..`, and cached children, skips hidden nodes and internal nodes for non-kernel credentials, updates access time, and tracks directory offsets.
- `devfs_fsync` is a no-op.
- `devfs_inactive` leaves normal unreferenced nodes cached, but immediately destroys stale unlinked nodes when the vnode count reaches zero.
- `devfs_fid` exposes `dv_ino`.
- `devfs_rwlock` and `devfs_rwunlock` bracket read/write/readdir and locking operations with `dv_contents`.
- `devfs_seek` rejects negative offsets.

Research notes:
- Attribute persistence logic is the main complexity in this file.
- `devfs_readdir` is side-effecting: it may configure devices by calling `dv_filldir`.
- The file documents the devfs/shadow namespace mapping for directories, minor nodes, and driver attributes, which is useful context for `/devices` path interpretation.
