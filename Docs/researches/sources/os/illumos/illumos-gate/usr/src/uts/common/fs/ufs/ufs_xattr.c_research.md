# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_xattr.c

## Role

`ufs_xattr.c` contains helper routines for UFS extended-attribute directory handling. It is small but important because UFS represents extended attributes through hidden/shadow attribute directories connected from a regular file or directory inode.

The file implements:
- `ufs_xattr_getattrdir()`
- `ufs_unhook_shadow()`

These routines are used by vnode paths such as `ufs_lookup()` and `ufs_l_pathconf()` in `ufs_vnops.c`.

## `ufs_xattr_getattrdir()`

`ufs_xattr_getattrdir(vnode_t *dvp, struct inode **sip, int flags, struct cred *cr)` locates or creates the attribute directory associated with `dvp`.

Behavior:
- Converts `dvp` to its inode with `VTOI()`.
- If `LOOKUP_XATTR` is set and `ip->i_oeftflag` is nonzero, it treats that field as the inode number of the attribute directory.
- Loads the attribute-directory inode with `ufs_iget()`.
- Verifies the loaded inode is actually `IFATTRDIR`.
- If verification fails, logs a note recommending fsck, releases the vnode, and returns `ENOENT`.
- Marks the attribute directory vnode as `VDIR` and sets `V_XATTRDIR`.
- If no attribute directory exists and `CREATE_XATTR_DIR` is set, creates it through `ufs_xattrmkdir()`.
- Otherwise returns `ENOENT`.

Important detail: the routine supports both lookup and creation depending on flags. It also allows creation when `CREATE_XATTR_DIR` is set even without `LOOKUP_XATTR`.

## `ufs_unhook_shadow()`

`ufs_unhook_shadow(struct inode *ip, struct inode *sip)` disconnects an empty attribute/shadow directory from its parent inode.

Preconditions:
- Caller must hold `sip->i_contents` as writer.
- Caller must hold `ip->i_contents` as writer.

Behavior:
- Returns immediately on read-only vnodes.
- Returns if either inode no longer has a UFS mount pointer.
- Takes the inode hash lock and both vnode locks.
- Only proceeds when the relevant vnodes are effectively unused; if both vnode counts are not 1, it returns without unhooking.
- Decrements the shadow inode link count by 2.
- Marks the shadow inode reclaimable with `ufs_setreclaim()`.
- Logs inode changes through `TRANS_INODE()`.
- Sets `ICHG`, increments `i_seq`, and updates times.
- Clears the parent inode’s `i_oeftflag`.
- Logs and marks the parent inode changed, increments `i_seq`, and synchronously updates the parent with `ufs_iupdat(ip, 1)`.

This is used to clean up empty extended-attribute directories, notably from `_PC_XATTR_EXISTS` handling in `ufs_l_pathconf()`.

## Dependencies

The file depends on UFS inode, filesystem, directory, transaction, quota, and panic headers:
- `ufs_inode.h`
- `ufs_fs.h`
- `ufs_fsdir.h`
- `ufs_trans.h`
- `ufs_panic.h`
- `ufs_quota.h`

It also uses vnode, VFS, DNLC/path, credentials, locking, VM segment, errno, debug, and kernel logging facilities.

## Important Behaviors and Invariants

- `i_oeftflag` is the parent inode field linking to the extended-attribute directory inode.
- Attribute directories must have inode type `IFATTRDIR`; otherwise the filesystem is considered inconsistent and fsck is recommended.
- Attribute-directory vnodes are exposed as directory vnodes with `V_XATTRDIR`.
- Shadow unhooking is conservative and avoids touching active vnodes.
- Link count and parent-pointer updates are transaction-aware.
- The function assumes callers already established correct `i_contents` write locking.

## Research Notes

This file provides the glue for UFS extended attributes rather than implementing full attribute-directory creation or directory-entry operations. The correctness-sensitive parts are validation of `i_oeftflag`, conservative vnode-count checks in `ufs_unhook_shadow()`, and the coordinated transaction updates to both the shadow inode and parent inode.
