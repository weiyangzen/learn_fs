# File Research: sources/os/linux/linux-stable/fs/ecryptfs/dentry.c

## Summary
Defines eCryptfs dentry operations for revalidating upper dentries against lower dentries and releasing lower dentry references.

## Main Responsibilities
- Reject RCU pathwalk revalidation with `-ECHILD`.
- Delegate revalidation to the lower dentry when the lower filesystem supplies `d_revalidate`.
- Refresh upper inode attributes from the lower inode for positive dentries.
- Invalidate upper dentries whose inode link count dropped to zero.
- Drop the lower dentry reference stored in `dentry->d_fsdata`.

## Key APIs
- `ecryptfs_d_revalidate()`
- `ecryptfs_d_release()`
- `ecryptfs_dops`

## Important Behavior
The revalidation path snapshots the lower dentry name before invoking the lower filesystem operation. For positive upper dentries, it mirrors lower attributes and returns invalid when the upper inode has no links.

## Research Notes
This file is small but part of the stackable-filesystem contract: every eCryptfs dentry owns a referenced lower dentry in `d_fsdata`, and dentry validity follows the lower filesystem.
