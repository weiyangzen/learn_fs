# File Research: sources/os/linux/linux-stable/fs/autofs/symlink.c

## Purpose
Implements autofs symlink inode operations.

## Main Interface
- `autofs_get_link()` via `autofs_symlink_inode_operations`.

## Important Behavior
`get_link` returns `-ECHILD` for RCU/pathwalk contexts without a dentry. For non-daemon accesses, it updates the associated `autofs_info::last_used` timestamp before returning the symlink target stored in `inode->i_private`.

## Cross-File Relationships
Symlink target strings are allocated in `autofs_dir_symlink()` and freed by `autofs_evict_inode()`. Last-used timestamps feed expiry decisions in `expire.c`.

## Risks / Review Notes
The symlink target is raw inode-private storage; lifetime is tied to inode eviction. RCU symlink resolution is not supported here.
