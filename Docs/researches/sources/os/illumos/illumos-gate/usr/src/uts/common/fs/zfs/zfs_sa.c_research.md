# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_sa.c

This file connects ZPL znodes to the ZFS System Attribute framework. Its global `zfs_attr_table[]` registers native ZPL attributes such as time fields, generation, mode, size, parent, links, xattr object, flags, UID/GID, ACL data, symlink data, scanstamp, and project ID.

`zfs_sa_readlink()` reads symlink contents from either the old znode bonus-buffer layout or from block zero of the object if the link does not fit in the legacy bonus area. `zfs_sa_symlink()` performs the corresponding write path: short symlinks are stored after `ZFS_OLD_ZNODE_PHYS_SIZE` in the bonus buffer, while longer symlinks grow the file block size, hold block zero, dirty it, and copy the target there.

`zfs_sa_get_scanstamp()` and `zfs_sa_set_scanstamp()` bridge the antivirus scanstamp optional attribute across both SA and legacy znode layouts. For SA znodes they use `sa_lookup()` or `sa_update()` on `SA_ZPL_SCANSTAMP`; for legacy znodes they store the scanstamp after the old znode physical structure and track presence with `ZFS_BONUS_SCANSTAMP` in `z_pflags`.

`zfs_sa_upgrade()` migrates an old-style znode bonus layout into SA form when possible. It skips symlinks and znodes without cached ACLs, avoids deadlocking on `z_lock`, bulk-reads old attributes, fills a new SA attribute template, transforms older ACLs to FUID-aware form if needed, preserves xattr and scanstamp data, changes the bonus type to `DMU_OT_SA`, replaces all SA attributes, frees any external ACL object, and marks `z_is_sa`.

`zfs_sa_upgrade_txholds()` adds the transaction holds needed for a possible SA upgrade: a general SA hold and, if an external ACL exists, a free hold for that object. This helper is used by mutation paths before they touch legacy znodes. Correctness depends on matching the SA registration table offsets expected by quota/project-accounting code and on upgrade callers taking adequate DMU transaction holds.
