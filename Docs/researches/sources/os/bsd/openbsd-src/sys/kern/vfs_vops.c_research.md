# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_vops.c

Purpose: Implements typed wrappers around vnode operation vectors, converting public `VOP_*()` calls into `struct vop_*_args` dispatches.

Key behavior:
- Provides wrappers for lookup, create, mknod, open, close, access, getattr, setattr, read, write, ioctl, kqfilter, revoke, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, abortop, inactive, reclaim, lock, unlock, bmap, strategy, bwrite, pathconf, and advisory locking.
- Returns `EOPNOTSUPP` when an operation is absent from the vnode’s `v_op` table.
- Uses `ASSERT_VP_ISLOCKED()` under `VFSLCKDEBUG` to validate lock expectations before operations that require locked vnodes.
- `VOP_REMOVE()` handles vnode release/unlock cleanup after filesystem remove completes.
- `VOP_FSYNC()` checks `VBIOERROR` after the filesystem sync operation and converts latent bio errors to `EIO`.
- `VOP_PATHCONF()` handles global constants such as `_PC_PATH_MAX`, `_PC_PIPE_BUF`, and async/prio/sync I/O before delegating.

Filesystem relevance:
- This file defines the core dispatch ABI between generic VFS code and concrete filesystem implementations.
- Lock assertions and cleanup conventions here affect every filesystem vnode operation.
