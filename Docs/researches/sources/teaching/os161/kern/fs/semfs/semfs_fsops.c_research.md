# File Research: sources/teaching/os161/kern/fs/semfs/semfs_fsops.c

Implements filesystem-level operations and bootstrap for `semfs`.

Main behavior:
- `semfs_sync` is a no-op because the filesystem is synthetic and memory-only.
- `semfs_getvolname` returns fixed volume name `"sem"`.
- `semfs_getroot` obtains the root vnode using `semfs_getvnode(SEMFS_ROOTDIR)`.
- `semfs_unmount` refuses unmount with `EBUSY` if any vnodes remain, then destroys all semaphores, direntries, arrays, and locks.
- `semfs_bootstrap` creates one `semfs` instance and registers it with VFS as `sem`.

Construction:
- Allocates `struct semfs`, table lock, vnode array, semaphore array, directory lock, and directory-entry array.
- Initializes `semfs_absfs.fs_data` and `fs_ops`.

Notable invariants:
- The filesystem is expected to be attached at boot and normally not remounted.
- `semfs_destroy` assumes no live vnodes remain and tears down all backing objects.
