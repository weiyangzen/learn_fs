# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ctldir.c

Implements the virtual ZFS control directory `.zfs`, including `.zfs/snapshot` and `.zfs/shares`. These nodes are built with illumos GFS primitives and do not exist as normal on-disk directory entries. Snapshot entries under `.zfs/snapshot` are GFS mountpoints that trigger kernel automounts of snapshot datasets.

Initialization and lifecycle are handled by `zfsctl_init()`, `zfsctl_fini()`, `zfsctl_create()`, `zfsctl_destroy()`, `zfsctl_root()`, and `zfsctl_is_node()`. The root `.zfs` vnode is cached in `zfsvfs->z_ctldir`, has synthetic inode/time attributes, and exposes two entries: `snapshot` and `shares`. The control vnodes reject write opens/access and provide FIDs suitable for NFS exposure.

The `.zfs/snapshot` implementation maintains an AVL tree of currently known or mounted snapshot entries (`zfs_snapentry_t`) protected by `sd_lock`. `zfsctl_snapdir_lookup()` validates and resolves snapshot names, handles case-insensitive real-name lookup, creates a GFS snapshot vnode when needed, mounts the ZFS snapshot on that vnode via `domount()`, traverses to the mounted root, and then rewrites the mounted root vnode’s `v_vfsp` to the parent filesystem for NFS compatibility. If a cached snapshot vnode was unmounted behind its back, lookup remounts it.

Snapshot mutation operations are implemented as directory operations on `.zfs/snapshot`. `zfsctl_snapdir_mkdir()` creates a snapshot after permission checks. `zfsctl_snapdir_remove()` unmounts and destroys a snapshot. `zfsctl_snapdir_rename()` renames a snapshot after resolving case variants and checking permissions, then updates both the AVL entry and mounted VFS resource/mountpoint strings with `zfsctl_rename_snap()`.

Directory enumeration uses `zfsctl_snapdir_readdir_cb()` to list snapshots directly from DMU snapshot iteration, including case-conflict flags when requested. Attribute reporting for `.zfs/snapshot` uses the number of cached mounted entries for link/size and the dataset snapshot cmtime for timestamps.

The `.zfs/shares` directory is a virtual pass-through to `zfsvfs->z_shares_dir` when configured. `zfsctl_shares_lookup()`, `zfsctl_shares_readdir()`, `zfsctl_shares_getattr()`, and `zfsctl_shares_fid()` delegate to the real shares directory znode; absent shares support returns `ENOTSUP`.

Unmount and cleanup paths are explicit. `zfsctl_unmount_snap()` force/unmounts a snapshot vfs, releases the GFS vnode without recursing into the snapdir inactive path, and frees the AVL entry. `zfsctl_snapshot_inactive()` removes an unused snapshot mountpoint vnode from the AVL tree. `zfsctl_lookup_objset()` maps a mounted snapshot objset ID back to its `zfsvfs_t`, and `zfsctl_umount_snapshots()` unmounts all mounted snapshots for a filesystem during parent unmount.

Key invariants: `.zfs` rejects extended-attribute lookup; snapshot mountpoint vnodes are expected to be covered and have almost no operations; recursive lookup while holding `sd_lock` returns `ENOENT` to avoid mount recursion; mounted snapshot roots deliberately masquerade as part of the parent VFS for NFS behavior.
