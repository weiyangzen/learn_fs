# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_dir.h

Declares ZFS directory-entry locking, lookup, link mutation, node creation/removal, unlinked-set draining, sticky-bit access, and xattr-directory helpers.

Key elements:
- `zfs_dirent_lock()` flags include `ZNEW`, `ZEXISTS`, `ZSHARED`, `ZXATTR`, `ZRENAMING`, `ZCILOOK`, `ZCIEXACT`, and `ZHAVELOCK`.
- Mknode flags: `IS_ROOT_NODE` and `IS_XATTR`.
- Declares link create/destroy, directory lookup, mknode/rmnode, name switching, empty-directory checks, unlinked drain control, sticky remove access, and xattr directory creation/get.

Main dependencies and interactions:
- Depends on pathname, DMU, and `zfs_znode.h`.
- Uses `zfs_dirlock_t`, `znode_t`, `zfsvfs_t`, `zfs_acl_ids_t`, and transactions.

Implementation notes:
- Directory operations are coupled with ZIL logging and znode-level name locks defined in `zfs_znode.h`.
