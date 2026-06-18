# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vfsops.c

Unionfs VFS mount operations implementation.

Key responsibilities:
- Registers unionfs as a loopback filesystem through `VFS_SET(..., VFCF_LOOPBACK)`.
- Implements mount parsing for target/from path, `below`, `udir`, `ufile`, root-only `uid`, `gid`, `copymode`, and `whiteout` options.
- Resolves and orders upper/lower root vnodes, builds `struct unionfs_mount`, copies upper read-only state, detects common self-deadlock cases, creates the unionfs root vnode, and registers upper-mount relationships.
- Sets mount flags and kernel flags including `MNT_LOCAL`, `MNTK_NOMSYNC`, `MNTK_UNIONFS`, and shared write behavior.
- Handles `VV_CROSSLOCK` for the `below` mount case.
- Implements unmount, root lookup, quota forwarding to the upper mount, statfs aggregation, sync no-op, unsupported vget/fhtovp/export, and extattrctl forwarding to the relevant layer.

Dependencies:
- Depends on FreeBSD VFS mount option parsing, namei, vnode locking, mount upper registration, statfs, quota, and extattr APIs.
- Depends on `unionfs_nodeget`, `unionfs_init`, and `unionfs_uninit` from `union_subr.c`.

Notable risks:
- Mount construction is sensitive to correct upper/lower ordering, especially with `below`.
- The self-deadlock detection is explicitly not exhaustive; nested unionfs/nullfs arrangements can still be risky.
- `VV_CROSSLOCK` handling must be paired correctly during unmount.
- Export/NFS file-handle operations are unsupported.
- Statfs combines lower block/file counts with upper writable/free values, which is intentionally synthetic rather than a true unified capacity model.
