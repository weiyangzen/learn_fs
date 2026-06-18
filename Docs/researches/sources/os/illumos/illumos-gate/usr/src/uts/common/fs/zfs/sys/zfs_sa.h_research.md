# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_sa.h

Defines ZPL system-attribute IDs, legacy znode physical layout, SA offsets, attribute registration tables, and SA helper prototypes.

Key elements:
- `zpl_attr_t` lists ZPL attributes such as times, generation, mode, size, parent, links, xattr, rdev, flags, uid/gid, ACL, symlink, scanstamp, and project ID.
- `ZFS_OLD_ZNODE_PHYS_SIZE` and `ZFS_SA_BASE_ATTR_SIZE` bridge legacy bonus-buffer layout to SA storage.
- Offset constants describe legacy attribute positions.
- `znode_phys_t` is the deprecated pre-ZPL-v5 physical znode layout.
- Kernel prototypes support SA readlink, symlink storage, upgrade, scanstamp get/set, and txholds.

Main dependencies and interactions:
- Kernel includes DMU, ZFS ACL, znode, SA, and ZIL.
- Works with `zfs_znode.h` macros that index `zfsvfs_t->z_attr_table`.

Implementation notes:
- Attribute enum values are not on-disk IDs; actual numeric IDs come from SA registration per filesystem.
