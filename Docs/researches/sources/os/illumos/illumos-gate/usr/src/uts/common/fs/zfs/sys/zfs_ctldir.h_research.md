# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ctldir.h

Declares the `.zfs` control directory interface, including snapshot control operations and synthetic control-node lookup helpers.

Key elements:
- `ZFS_CTLDIR_NAME` is `.zfs`.
- `zfs_has_ctldir()` checks whether a root znode has an attached control directory.
- `zfs_show_ctldir()` also checks the mount setting controlling visibility.
- Declares create/destroy/init/fini, root lookup, snapshot rename/destroy/unmount, FID creation, and objset lookup functions.
- Defines synthetic inode constants `ZFSCTL_INO_ROOT` and `ZFSCTL_INO_SNAPDIR`.

Main dependencies and interactions:
- Depends on pathname, vnode, `zfs_vfsops.h`, and `zfs_znode.h`.
- Bridges root-directory lookup behavior with mounted snapshot handling.

Implementation notes:
- The macros assume a `znode_t` with `z_zfsvfs`, `z_root`, `z_ctldir`, and `z_show_ctldir`.
