# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dir2_readdir.c

## Purpose
Implements XFS `readdir` support for shortform, block, leaf, and node directory formats, translating XFS directory entries into VFS `dir_context` emissions.

## Main APIs
- `xfs_dir3_get_dtype` maps XFS filetype values to VFS `DT_*`, returning `DT_UNKNOWN` when unsupported or invalid.
- `xfs_readdir` is the public entry point; it validates shutdown/zapped state, builds DA args, chooses the directory format, and dispatches to format-specific walkers.

## Format Walkers
Shortform readdir emits `.` and `..`, then walks local entries in the inode fork. Block readdir reads the single block directory, drops the inode data-map lock while emitting, skips unused regions, checks names, and emits entries. Leaf/node readdir scans mapped data blocks below `XFS_DIR2_LEAF_OFFSET`, uses a sliding readahead window, and handles sparse mappings.

## Cookies and Locking
Directory positions use XFS dataptrs masked to 31 bits for VFS cookies. Leaf/node walking reacquires the data-map lock only to read mappings and releases it before processing buffers. Optional transactions collect buffer releases without dirtying metadata.

## Corruption Handling
All walkers validate names with `xfs_dir2_namecheck`; invalid names mark the directory data fork sick and return `-EFSCORRUPTED`. Shutdown or zapped forks return `-EIO`.
