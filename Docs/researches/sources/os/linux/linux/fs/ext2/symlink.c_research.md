# File Research: sources/os/linux/linux/fs/ext2/symlink.c

## Purpose
Defines inode operations for ext2 symlinks.

## Main Responsibilities
- `ext2_symlink_inode_operations` uses `page_get_link` for regular symlinks stored through page/cache-backed data.
- `ext2_fast_symlink_inode_operations` uses `simple_get_link` for fast symlinks stored directly in inode data.
- Both operation tables expose ext2 `getattr`, `setattr`, and `listxattr`.

## Integration Points
Used by inode creation/loading code to attach the right symlink behavior depending on whether the symlink is fast or block-backed. Integrates with ext2 xattr listing so symlinks can expose extended attributes.

## Risks and Edge Cases
This file is intentionally minimal; correctness depends on inode code selecting the matching operations table for fast versus non-fast symlinks.
