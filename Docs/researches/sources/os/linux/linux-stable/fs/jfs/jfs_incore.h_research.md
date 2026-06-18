# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_incore.h

This header defines the JFS in-memory inode and superblock private structures plus helper macros for locks, commit flags, and type-safe accessors.

Key responsibilities:
- Defines `JFS_SUPER_MAGIC`.
- Defines `struct jfs_inode_info`, embedding the VFS inode plus JFS-specific inode metadata: fileset, mode flags, saved uid/gid, inode extent descriptor, ACL/EA descriptors, creation time, directory index state, inode map pointer, commit flags, allocation group state, transaction lock IDs, synchronization primitives, quota pointers, device number, and type-specific inline storage.
- Overlays type-specific inode data through a union: regular files use an xtree root and inode-map pointer; directories use inline directory-table slots and a dtree root; symlinks/xattrs use inline data buffers.
- Defines lock helpers for the per-inode read/write semaphore and documents why it is redundant for directory mutation under VFS directory locking.
- Defines JFS commit flags such as dirty inode state, inline EA changes, directory-table changes, stale extents, and sync-list metadata.
- Defines lock subclass enums for commit mutex and read/write lock nesting.
- Defines `struct jfs_sb_info`, holding mount-wide state such as metadata inodes, log pointer, block size geometry, aggregate/log descriptors, UUIDs, commit state, inode generation/inostamp, block map, NLS table, recovery state, mount flags, uid/gid/umask overrides, and trim settings.
- Provides `JFS_IP()`, `JFS_SBI()`, `jfs_dirtable_inline()`, and `isReadOnly()` helpers.

Important interactions:
- Included by nearly every JFS implementation file.
- Pulls in xtree and dtree definitions because those roots are embedded directly in the inode-private union.
- Connects transaction code, inode-map code, directory code, extent code, quota, and VFS inode lifecycle through shared private state.

Notable invariants and risks:
- The unioned inline areas mirror on-disk dinode layout assumptions; wrong type interpretation can corrupt xtree roots, dtree roots, inline symlinks, or inline EAs.
- `commit_mutex` must be taken after starting a transaction, per the comment, because dirty inode commit can occur while another transaction waits.
- `jfs_dirtable_inline()` depends on `next_index` and the inline directory-table capacity; dtree code uses this to decide whether directory cookies live in the inode or in an xtree-backed table.
- `isReadOnly()` is tied to the presence of a log pointer, not directly to VFS mount flags.

Research notes:
- This is the main in-memory object model for JFS. Most cross-file behavior in this group passes through fields declared here.
