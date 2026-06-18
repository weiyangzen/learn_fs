# File Research: sources/os/linux/linux/fs/autofs/symlink.c

## Summary
Implements symlink inode operations for autofs dentries.

## Main Responsibilities
- Return the symlink target stored in `inode->i_private`.
- Update autofs last-used time for non-daemon access.

## Key APIs
- `autofs_symlink_inode_operations`.
- `autofs_get_link()`.

## Important Behavior
RCU link lookup without a dentry returns `-ECHILD`. Non-oz-mode access updates `ino->last_used`, which affects expiration eligibility.

## Risks
The symlink target lifetime is owned by the inode and freed from `autofs_evict_inode()`. Expiry behavior depends on `last_used` being updated on ordinary access.
