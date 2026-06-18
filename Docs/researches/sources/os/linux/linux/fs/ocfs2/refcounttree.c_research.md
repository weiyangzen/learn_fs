# File Research: sources/os/linux/linux/fs/ocfs2/refcounttree.c

`refcounttree.c` implements OCFS2’s shared-extent reference count trees, copy-on-write, reflink creation, xattr CoW, and range remap helpers. It is the core of OCFS2’s reflink/refcount feature.

Main responsibilities:
- Maintains in-memory refcount tree objects:
  - `struct ocfs2_refcount_tree` instances are cached in `osb_rf_lock_tree`, keyed by refcount root block.
  - Each tree has kref lifetime management, an OCFS2 lock resource, an rw semaphore, metadata cache operations, and an LRU shortcut.
  - Generation checks in `ocfs2_lock_refcount_tree()` detect refcount block reuse and recreate stale in-memory lock objects safely.
- Validates and reads refcount blocks with signature, block number, fs generation, and ECC checks.
- Creates, attaches, and removes refcount trees:
  - `ocfs2_create_refcount_tree()` allocates a refcount root block and marks the inode `OCFS2_HAS_REFCOUNT_FL`.
  - `ocfs2_set_refcount_tree()` attaches another inode to an existing tree and increments root `rf_count`.
  - `ocfs2_remove_refcount_tree()` decrements `rf_count`, clears inode flags, and frees the root block when the last owner is gone.
  - `ocfs2_try_remove_refcount_tree()` removes empty trees only when data and externally stored xattrs are gone.
- Manages refcount records:
  - `ocfs2_get_refcount_rec()` finds a real or fake zero-refcount record covering a physical cluster range.
  - insert, split, merge, increase, and decrease paths keep records sorted, coalesce adjacent records with equal counts, and remove zero-count records.
  - Inline refcount roots expand into a refcount btree when record capacity is exhausted.
  - Leaf splitting sorts by low 32-bit cpos to find a btree split key, then restores full 64-bit ordering.
  - Empty leaf blocks are removed from the refcount btree and queued for deferred deallocation.
- Calculates metadata and journal credit needs for refcount changes, including worst-case record splitting and refcount tree expansion.
- Implements CoW:
  - `ocfs2_refcount_cal_cow_clusters()` chooses a CoW range, preferring boundaries up to `MAX_CONTIG_BYTES` for better I/O layout.
  - `ocfs2_lock_refcount_allocators()` reserves metadata and optional replacement data clusters.
  - `ocfs2_make_clusters_writable()` handles refcount 1 by clearing the refcount flag, and refcount >1 by allocating new clusters, copying data, replacing extent mappings, and decrementing old refcounts.
  - Data copying can use page-cache/folio mapping (`ocfs2_duplicate_clusters_by_page()`) or journaled buffer copying (`ocfs2_duplicate_clusters_by_jbd()`).
  - `ocfs2_refcount_cow()` loops over file extents and CoWs any refcounted range before write.
- Supports xattr refcounting:
  - `ocfs2_refcounted_xattr_delete_need()` estimates resources needed to delete refcounted xattr value extents.
  - `ocfs2_refcount_cow_xattr()` performs CoW on xattr value extent trees and supports post-refcount callbacks.
  - `ocfs2_attach_refcount_tree()` also attaches xattrs to the tree when a file becomes refcounted.
- Implements reflink creation:
  - `ocfs2_reflink_ioctl()` resolves source and target paths and dispatches to `ocfs2_vfs_reflink()`.
  - `ocfs2_reflink()` creates the target as an orphan first, reflinks data/xattrs, initializes security/ACL when not preserving attributes, then moves the orphan into the target directory.
  - `ocfs2_attach_refcount_tree()` ensures the source has a refcount tree and marks all existing extents refcounted.
  - `ocfs2_create_reflink_node()` attaches the target to the source tree, copies inline data or duplicates extent mappings, and increments refcounts.
  - `ocfs2_complete_reflink()` copies source attributes, size, dynamic features, and optionally ownership/mode/mtime.
- Implements remap helpers:
  - `ocfs2_reflink_remap_blocks()` prepares shared refcount-tree ownership between source and destination, converts destination inline data to extents when needed, and remaps a range.
  - `ocfs2_reflink_remap_extent()` punches destination ranges, marks source extents refcounted if necessary, inserts destination shared extents, and returns partial progress.
  - `ocfs2_reflink_update_dest()` grows destination size and updates timestamps after remap.
  - `ocfs2_reflink_inodes_lock()` / `ocfs2_reflink_inodes_unlock()` lock two inodes in stable order using VFS locks, OCFS2 rw locks, and inode cluster locks.

Key invariants:
- Refcount tree mutation requires the refcount cluster lock and tree semaphore.
- Refcount records describe physical clusters, while inode extent trees describe logical file clusters; the code carefully translates between them.
- Data extents are marked `OCFS2_EXT_REFCOUNTED` only after corresponding refcount records exist or are created in the same transaction.
- CoW must update data extents and decrease old refcounts atomically under journaling.
- Distinct refcount trees are not merged; range remap rejects source/destination pairs with different existing trees.
- Extent caches are truncated after refcount/CoW changes because cached physical mappings may be stale.
