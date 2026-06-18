# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vfsops.c

This file implements nullfs mount-level VFS operations.

Key mount behavior:
- Rejects mounting nullfs as root.
- Treats update mounts as a no-op except for NFS export updates.
- Accepts mount target from `from` or `target`.
- Temporarily unlocks a covered nullfs vnode in one nesting case to reduce deadlock risk.
- Resolves and locks the lower root vnode with `namei()`.
- Rejects self-mounts and certain multi-null mount cases that would lock against themselves.
- Requires the lower root vnode to be `VDIR` or `VREG` and match the covered vnode type.
- Registers the upper mount with the lower mount using `vfs_register_upper_from_vp()`.
- Creates the root alias with `null_nodeget()`.
- Enables vnode caching based on mount options, sysctl default, and lower-mount `MNTK_NULL_NOCACHE`.
- Optionally registers lower-mount notification callbacks for cached vnode invalidation.
- Propagates relevant mount flags such as local status and buffer/cache capabilities.

Options and tunables:
- `vfs.nullfs.cache_vnodes`: default cache policy.
- Mount options: `cache`, `nocache`, `unixbypass`, `nounixbypass`.

Other VFS operations:
- `nullfs_unmount()` flushes vnodes, unregisters notifications/upper mount linkage, clears cross-lock state, releases lower root, and frees mount data.
- `nullfs_root()` vgets the lower root and returns/create the upper alias.
- `nullfs_quotactl()` forwards quota operations to the lower mount while carefully unbusying the upper mount.
- `nullfs_statfs()` copies selected fields from lower `VFS_STATFS`.
- `nullfs_vget()` and `nullfs_fhtovp()` map lower returned vnodes to nullfs aliases.
- `nullfs_extattrctl()` forwards extended attribute control to the lower mount.
- `nullfs_reclaim_lowervp()` and `nullfs_unlink_lowervp()` are lower-vnode notification handlers that reclaim/drop upper aliases.

Research-relevant risks:
- Mount and unmount paths carry explicit comments about deadlock-prone relocking.
- Cache-enabled mounts depend on lower mount notification to avoid stale aliases.
- `nullfs_unlink_lowervp()` manipulates references/holds and lock ownership differently for doomed and non-doomed vnodes.
