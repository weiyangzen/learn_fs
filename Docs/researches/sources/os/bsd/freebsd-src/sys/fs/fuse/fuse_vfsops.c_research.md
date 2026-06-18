# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vfsops.c

This file implements the `fusefs` VFS operation vector: mount, unmount, root lookup, statfs, vnode lookup by inode/filehandle, and FUSE device validation.

Key responsibilities:
- Defines `struct vfsops fuse_vfsops` with:
  - `vfs_fhtovp`
  - `vfs_mount`
  - `vfs_unmount`
  - `vfs_root`
  - `vfs_statfs`
  - `vfs_vget`
- Defines privilege aliases for FUSE-specific mount behaviors.
- Exposes sysctl `vfs.fusefs.enforce_dev_perms`.
- Defines `M_FUSEVFS`.
- Validates the FUSE device in `fuse_getdevice`.
  - Looks up the mount `from` path.
  - Requires a character device.
  - Optionally checks read/write access to the device.
  - Requires device switch name `"fuse"`.
  - Takes a device reference for mount lifetime.
- Parses mount options in `fuse_vfsop_mount`.
  - Requires `fspath`, `from`, and `fd`.
  - Supports option aliases with normal and `__`-prefixed forms:
    - `allow_other`
    - `push_symlinks_in`
    - `default_permissions`
    - `intr`
    - `auto_unmount`
  - Parses `max_read`, `linux_errnos`, `timeout`, and `subtype`.
  - Clamps daemon timeout to allowed min/max.
- Handles remounts through `fuse_vfs_remount`.
  - Rejects changes to mount ownership and FUSE session options.
  - Revalidates dead state and permissions.
- Establishes a new mount.
  - Opens the passed file descriptor with read capability.
  - Retrieves `struct fuse_data` from `devfs` cdevpriv.
  - Checks daemon ownership and privileges, including `allow_other`.
  - Stores mount pointer, flags, max read, timeout, errno mode, and mount flags in `struct fuse_data`.
  - Sets `mp->mnt_data`.
  - Marks filesystem non-local, using buffer cache, and disables nullfs caching.
  - Sets I/O sizes and display names.
  - Sends initial `FUSE_INIT`.
  - On failure, releases acquired session/device references.
- Implements unmount in `fuse_vfsop_unmount`.
  - Drops the extra root vnode reference.
  - Flushes vnodes with `vflush`, forcing close when requested.
  - Sends `FUSE_DESTROY` when daemon may implement it.
  - Marks the session dead.
  - Clears mount data, drops session/device references.
- Implements export/filehandle lookup.
  - `fuse_vfsop_fhtovp` requires `FSESS_EXPORT_SUPPORT`, calls `VFS_VGET`, and checks generation.
  - `fuse_vfsop_vget` requires export support, tries cached vnode lookup, then performs `FUSE_LOOKUP` of `"."` using the inode as parent node id.
  - Validates that `"FILE/."` returns the same node id.
  - Instantiates/caches vnode and attrs when safe relative to `last_local_modify`.
- Implements root lookup in `fuse_vfsop_root`.
  - Reuses cached `data->vroot` when present.
  - Otherwise creates root vnode with `FUSE_ROOT_ID`, stores an extra reference, and handles races.
- Implements `statfs` in `fuse_vfsop_statfs`.
  - Sends `FUSE_STATFS` after init.
  - Copies daemon `fuse_kstatfs` fields into FreeBSD `statfs`.
  - Returns a fake empty statfs when uninitialized or daemon is dead with `ENOTCONN`, preserving path-based unmount usability.

Integration points:
- Mount flow consumes `/dev/fuse` cdevpriv created by the device layer outside this group.
- Uses IPC dispatchers to send `FUSE_INIT`, `FUSE_DESTROY`, `FUSE_LOOKUP`, and `FUSE_STATFS`.
- Uses node helpers for root and export vnode creation.
- Uses FreeBSD VFS hash/namecache and NFS export interfaces.

Notable risks and research hooks:
- `FUSE_INIT` is sent asynchronously during mount; other ticket allocation waits for init completion based on session flags.
- Remount currently rejects most useful option changes.
- Export support is only allowed when negotiated; otherwise filehandle lookup returns extended `EOPNOTSUPP`.
- `vget` by inode depends on daemon support for lookup of `"."` by node id and, for NFS correctness, stable nodeid/generation behavior.
- Mount security is split between device permissions, daemon credential matching, and privilege checks for `allow_other` or mounting as a different user.
