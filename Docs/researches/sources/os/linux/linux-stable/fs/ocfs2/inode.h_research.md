# File Research: sources/os/linux/linux-stable/fs/ocfs2/inode.h

Purpose: defines OCFS2's inode-private structure, inode-private flags, inode access macros, inode lifecycle/read/validate prototypes, metadata-cache conversion helpers, and small inline inode utilities.

Read coverage: complete file read, 173 lines.

Key structures and constants:
- `struct ocfs2_inode_info` embeds `struct inode vfs_inode` and stores OCFS2 block identity, RW/meta/open lock resources, allocation and xattr semaphores, spin-protected open/I/O/cluster fields, dynamic features, inode attributes, unwritten extent list, orphan recovery link, metadata cache, extent map, JBD2 inode, directory lookup hints, local allocation reservation, fsync transaction ids, and quota pointers.
- `OCFS2_INODE_*` flags distinguish system, journal, bitmap, deleted, maybe-orphaned, direct-I/O-open, skip-orphan-dir, and DIO-orphan-entry states.
- `OCFS2_FI_FLAG_*` constants select special `ocfs2_iget()` behavior for system files, orphan recovery, and filecheck check/fix operations.

Declared behavior:
- Exposes `ocfs2_ilookup()`, `ocfs2_iget()`, `ocfs2_inode_revalidate()`, `ocfs2_populate_inode()`, `ocfs2_refresh_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_evict_inode()`, and inode block read/validation helpers.
- Publishes `ocfs2_aops` and `ocfs2_inode_caching_ops`.
- `ocfs2_inode_sector_count()` converts in-memory cluster count into 512-byte sector count.
- `ocfs2_is_refcount_inode()` tests the reflink/refcount dynamic feature.

Concurrency and lifetime:
- Header documents lock ownership by field: `ip_alloc_sem` protects allocation changes, `ip_xattr_sem` protects xattr changes, `ip_lock` protects selected counters/flags, and `recovery_lock` protects `ip_next_orphan`.
- Inode metadata cache access goes through `INODE_CACHE()` and `cache_info_to_inode()`.

Important dependencies:
- Includes `extent_map.h` and relies on OCFS2 lock resources, allocation reservations, caching info, extent maps, JBD2 inode state, and Linux quota structures.

Risk and edge cases:
- Consumers must not treat all `ip_flags` as spinlock-free; several fields are explicitly protected by `ip_lock`.
- `ocfs2_inode_sector_count()` assumes the inode's superblock cluster size is at least sector-sized and uses `ip_clusters`, not `i_size`.
- `ocfs2_is_refcount_inode()` reflects the in-memory dynamic feature copy; callers need a refreshed/locked inode when correctness depends on current on-disk state.
