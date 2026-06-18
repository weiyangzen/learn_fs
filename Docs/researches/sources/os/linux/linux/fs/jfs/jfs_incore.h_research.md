# File Research: sources/os/linux/linux/fs/jfs/jfs_incore.h

## Role

Defines JFS private in-core inode and superblock structures, lock helpers, commit flags, and core accessor functions.

## Key Responsibilities

- Defines `JFS_SUPER_MAGIC`.
- Defines `struct jfs_inode_info`, embedding Linux `struct inode` plus JFS fields for fileset, mode flags, saved uid/gid, inode extent descriptor, ACL/EA descriptors, creation time, directory index state, AG placement, transaction state, locks, and type-specific inline metadata.
- Provides inode union storage for regular-file xtree root plus imap pointer, directory inline table plus dtree root, and symlink/inline-EA data.
- Defines aliases such as `i_xtroot`, `i_imap`, `i_dirtable`, `i_dtroot`, `i_inline`, and `i_inline_ea`.
- Provides read/write lock macros for inode metadata serialization using `rdwrlock`.
- Defines commit flags for zero-link commit, inline EA commit, free-WMAP, dirty state, dirtable commit, stale extents, and sync-list metadata.
- Defines lockdep nesting classes for commit mutexes and rdwrlocks.
- Provides cflag bit operations.
- Defines `struct jfs_sb_info`, storing mount flags, metadata inodes, log state, block-size geometry, aggregate IDs, log/fsck/AIT descriptors, UUIDs, inode generation state, block map, NLS table, mount overrides, and discard settings.
- Provides `JFS_IP()`, `JFS_SBI()`, `jfs_dirtable_inline()`, and `isReadOnly()` helpers.

## Important Interactions

- Includes `jfs_xtree.h` and `jfs_dtree.h` because inline roots live directly in the private inode.
- Used by nearly every JFS implementation file as the bridge between Linux VFS objects and JFS metadata.
- `isReadOnly()` treats absence of a log pointer as read-only behavior for metadata update paths.
- `jfs_dirtable_inline()` controls when directory index table storage transitions from inode-inline slots to an xtree-backed table.

## Invariants and Risks

- The private inode union overlays file, directory, and symlink metadata; callers must use the branch matching inode mode.
- `commit_mutex` must be acquired after transaction begin, per comment, to avoid dirty-inode commit races.
- `rdwrlock` is used for xtree and special-inode synchronization; directory operations rely primarily on VFS directory locking.
- Mount uid/gid/umask overrides are stored in the superblock and interpreted during dinode copy in/out.
