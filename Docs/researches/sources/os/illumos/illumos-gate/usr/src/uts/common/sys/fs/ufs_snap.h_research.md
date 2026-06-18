# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_snap.h

## Role

Declares UFS snapshot ioctl helpers and snapshot constants.

## Key Definitions

- Debug level flags:
  - `UFSSNAPDB_CREATE`
  - `UFSSNAPDB_DELETE`
- `UFS_MAX_SNAPBACKFILESIZE` is `1LL << 39`, a 512 GB maximum backing file size.

## Interfaces

Kernel-visible functions:
- `ufs_snap_create(struct vnode *, struct fiosnapcreate_multi *, cred_t *)`
- `ufs_snap_delete(struct vnode *, struct fiosnapdelete *, cred_t *)`

These depend on `fssnap_if.h`, vnode, and credential types.

## Risk Notes

Snapshot create/delete touches filesystem consistency and backing-file limits. The maximum backing-file constant is part of UFS snapshot policy.
