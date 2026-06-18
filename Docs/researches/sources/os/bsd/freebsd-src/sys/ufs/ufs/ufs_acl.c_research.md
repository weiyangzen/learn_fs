# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_acl.c

## Purpose
Implements UFS ACL vnode operations and internal helpers for POSIX.1e and NFSv4 ACLs. The implementation stores nontrivial ACL state in UFS extended attributes and synchronizes relevant permission bits with the inode mode.

## Key Contents
Compiled under `#ifdef UFS_ACL`.

- Feature registration:
  - `FEATURE(ufs_acl, "ACL support for UFS")`
- POSIX.1e synchronization:
  - `ufs_sync_acl_from_inode`
    - Updates ACL entries from inode mode.
    - Updates `ACL_USER_OBJ`, `ACL_OTHER`, and either `ACL_MASK` or `ACL_GROUP_OBJ`.
  - `ufs_sync_inode_from_acl`
    - Computes mode bits from ACL and writes both in-core inode mode and dinode mode.
- NFSv4 ACL get path:
  - `ufs_getacl_nfs4_internal`
    - Reads NFSv4 ACL from extended attribute.
    - If absent, synthesizes trivial ACL from inode mode and owner.
    - Validates exact ACL size and calls `acl_nfs4_check`.
  - `ufs_getacl_nfs4`
    - Requires `MNT_NFS4ACLS`.
    - Requires `VREAD_ACL`.
- POSIX.1e ACL get path:
  - `ufs_get_oldacl`
    - Reads access/default ACL from extended attributes.
    - Validates stored `oldacl` size.
  - `ufs_getacl_posix1e`
    - Requires `MNT_ACLS`.
    - For absent access ACL, synthesizes minimal user/group/other ACL.
    - For absent default ACL, returns an empty ACL.
    - Converts old ACL storage format into `struct acl`.
    - Synchronizes access ACL from inode mode.
  - `ufs_getacl`
    - Dispatches to NFSv4 or POSIX.1e based on ACL type and mount flags.
- NFSv4 ACL set path:
  - `ufs_setacl_nfs4_internal`
    - Removes trivial ACL extended attribute or writes nontrivial ACL.
    - Maps `ENOATTR` to `EOPNOTSUPP`.
    - Updates mode from ACL, marks inode changed, posts vnode note, calls `UFS_UPDATE`.
  - `ufs_setacl_nfs4`
    - Requires `MNT_NFS4ACLS`, writable mount, non-null ACL.
    - Validates with `VOP_ACLCHECK`.
    - Rejects immutable/append-only inodes.
    - Requires `VWRITE_ACL`.
    - Reserves ACL entry headroom for chmod canonicalization.
- POSIX.1e ACL set/delete path:
  - `ufs_setacl_posix1e`
    - Requires `MNT_ACLS`.
    - Validates set ACLs with `VOP_ACLCHECK`.
    - Allows deletion only for default ACLs on directories.
    - Requires writable mount, non-immutable/non-append inode, and `VADMIN`.
    - Stores access/default ACLs via extended attributes.
    - Removes default ACL if requested.
    - Updates inode mode only after access ACL storage succeeds.
  - `ufs_setacl`
    - Dispatches to NFSv4 or POSIX.1e.
- ACL validation:
  - `ufs_aclcheck_nfs4`
    - Requires `MNT_NFS4ACLS`.
    - Enforces chmod headroom.
    - Calls `acl_nfs4_check`.
  - `ufs_aclcheck_posix1e`
    - Requires `MNT_ACLS`.
    - Allows access ACLs for all objects, default ACLs only for directories.
    - Enforces `OLDACL_MAX_ENTRIES`.
    - Calls `acl_posix1e_check`.
  - `ufs_aclcheck`
    - Handles mount validation and dispatch.

## Interactions
- Relies on `vn_extattr_get`, `vn_extattr_set`, and `vn_extattr_rm`.
- Uses inode mode helpers from `inode.h`.
- Depends on mount flags `MNT_ACLS` and `MNT_NFS4ACLS`.
- Extended attribute absence is sometimes interpreted as “ACL not present” and sometimes mapped to “operation not supported,” depending on path.
