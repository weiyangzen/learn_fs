# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/acl.h

## Purpose
Declares UFS-specific ACL entry points for kernel builds, including POSIX.1e ACL vnode operations and internal NFSv4 ACL helpers.

## Key Contents
- Forward declaration:
  - `struct inode`
- Internal NFSv4 ACL helpers:
  - `ufs_getacl_nfs4_internal(struct vnode *, struct acl *, struct thread *)`
  - `ufs_setacl_nfs4_internal(struct vnode *, struct acl *, struct thread *)`
- POSIX.1e synchronization helpers:
  - `ufs_sync_acl_from_inode(struct inode *, struct acl *)`
  - `ufs_sync_inode_from_acl(struct acl *, struct inode *)`
- VOP ACL entry points:
  - `ufs_getacl`
  - `ufs_setacl`
  - `ufs_aclcheck`

## Interactions
- Implemented in `ufs_acl.c`.
- Depends on UFS extended attributes for ACL storage.
- Bridges ACL state with inode mode bits.
