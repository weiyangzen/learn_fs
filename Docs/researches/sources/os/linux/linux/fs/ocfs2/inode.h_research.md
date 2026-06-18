# File Research: sources/os/linux/linux/fs/ocfs2/inode.h

`inode.h` defines OCFS2’s private inode structure, inode state flags, inode-cache helpers, and public inode lifecycle APIs.

Main contents:
- Defines `struct ocfs2_inode_info`, embedding the VFS inode and adding OCFS2 state:
  - On-disk block identity `ip_blkno`.
  - Cluster lock resources for metadata, open, and rw locks.
  - Allocation and xattr semaphores.
  - Spinlock-protected open count, cluster count, flags, attributes, I/O marker lists, and unwritten extent list.
  - Metadata cache, extent map, JBD2 inode, directory lookup hints, local allocation reservation, quota pointers, and fsync transaction IDs.
- Defines `ip_flags` values for system files, journal inodes, bitmap inodes, deleted inodes, maybe-orphaned remote unlinks, direct-I/O open state, orphan-dir skipping, and DIO orphan entries.
- Provides `OCFS2_I()` and `INODE_CACHE()` conversion helpers.
- Declares `ocfs2_evict_inode()`, `ocfs2_iget()`, `ocfs2_ilookup()`, inode revalidation, inode population/refresh, dirty marking, inode flag sync helpers, dinode validation, and inode block read helpers.
- Defines iget flags for system-file lookup, orphan recovery, and filecheck check/fix modes.
- Provides `ocfs2_inode_sector_count()` and `ocfs2_is_refcount_inode()` helpers.

This header is the contract shared by nearly all OCFS2 subsystems that need inode state, cluster locking, extent maps, journaling state, or metadata caching.
