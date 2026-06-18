# File Research: sources/os/linux/linux/fs/ecryptfs/dentry.c

## Purpose
Defines eCryptfs dentry operations for revalidation and lower-dentry lifetime release.

## Main Responsibilities
- `ecryptfs_d_revalidate()` delegates revalidation to the lower dentry when needed.
- Mirrors lower inode attributes into the upper inode on positive dentries.
- Invalidates positive upper dentries whose inode link count drops to zero.
- `ecryptfs_d_release()` drops the lower dentry stored in `d_fsdata`.

## Control Flow
On dcache revalidation, RCU lookup is rejected with `-ECHILD`. If the lower dentry has `DCACHE_OP_REVALIDATE`, the function snapshots the lower name and calls the lower dentry operation with the lower parent inode. For positive upper dentries, it copies all lower attributes up and returns invalid if `i_nlink` is zero.

## Dependencies
- `ecryptfs_dentry_to_lower()` and `ecryptfs_inode_to_lower()` from the shared header.
- VFS dentry APIs and `fsstack_copy_attr_all()`.

## Risks and Notes
- The file assumes `d_fsdata` is always a valid lower dentry for live eCryptfs dentries.
- RCU lookup fallback is required because the lower revalidation path may sleep.
