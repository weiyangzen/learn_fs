# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.c

This file provides inode utility operations for flag conversion, inode initialization, inherited policy, unlinked-list management, link-count updates, and inode teardown.

Major responsibilities:
- Convert FS_XFLAG values to `di_flags` and `di_flags2`.
- Convert in-core XFS inode flags back to FS_XFLAG values.
- Determine initial project ID inheritance.
- Inherit inode flags and COW extent-size flags from parent directories.
- Initialize newly allocated inodes through `xfs_inode_init`.
- Decide whether a new inode needs an attr fork, especially for parent pointers.
- Maintain AGI-backed unlinked inode lists with in-core backrefs.
- Add/remove inodes from unlinked lists via `xfs_iunlink` and `xfs_iunlink_remove`.
- Drop and bump link counts with transaction logging.
- Free/reset inodes with `xfs_inode_uninit`.

Important behavior:
- Directory inheritance propagates realtime, extent-size, project, noatime, nodump, sync, nosymlinks, nodefrag, and filestream policy.
- Regular-file inheritance can turn directory RTINHERIT/EXTSZINHERIT into REALTIME/EXTSIZE.
- Invalid inherited extent-size or COW extent-size hints are cleared to prevent verifier or allocator problems.
- New inodes may get an empty attr fork immediately if xattrs will be set or parent pointers are enabled.
- The unlinked-list implementation uses on-disk AGI bucket heads plus in-memory doubly linked backrefs, avoiding per-AG list-head arrays.

Risk notes:
- AGI unlinked-list corruption is treated as filesystem metadata sickness.
- Link counts are pinned at `XFS_NLINK_PINNED` on underflow/overflow-like boundary cases.
- Inode freeing orders `xfs_difree` before unlinked-list removal to preserve AGI lock ordering.
