# File Research: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.c

Purpose: implements OCFS2 refcount trees, copy-on-write, reflink creation/remapping, refcounted xattr handling, and shared extent reference-count mutation.

Read coverage: complete file read, 4806 lines.

Key structures:
- `struct ocfs2_cow_context` bundles inode, target COW range, data extent tree, refcount tree/root, allocators, deferred deallocation, optional xattr object, and cluster-duplication callbacks.
- Refcount trees are represented by `struct ocfs2_refcount_tree` from the header and cached in `osb->osb_rf_lock_tree`, with an LRU pointer for repeated lookup.
- Refcount records store physical cluster positions, cluster counts, and reference counts; roots can be inline record lists or extent-tree roots pointing to leaf refcount blocks.

Refcount tree lifetime:
- `ocfs2_validate_refcount_block()` checks ECC, signature, block number, and filesystem generation.
- `ocfs2_get_refcount_tree()` finds or creates an in-memory tree object, reads the root block generation, initializes its lock resource, and inserts it in the rb-tree cache.
- `ocfs2_lock_refcount_tree()` takes the DLM refcount lock plus local `rf_sem`, reads the root, and detects root-block generation reuse; stale in-memory trees are removed and recreated.
- `ocfs2_create_refcount_tree()` allocates and initializes a new refcount root block, marks the inode `OCFS2_HAS_REFCOUNT_FL`, records `i_refcount_loc`, and inserts the new tree cache entry.
- `ocfs2_set_refcount_tree()` attaches another inode to an existing tree and increments root `rf_count`.
- `ocfs2_remove_refcount_tree()` clears inode refcount state, decrements root `rf_count`, and frees the root block when the last inode detaches.
- `ocfs2_try_remove_refcount_tree()` removes a now-unused refcount tree only when data clusters and refcounted external xattrs are gone.

Refcount record mutation:
- `ocfs2_get_refcount_rec()` locates the record or hole covering a physical cluster range, reading tree leaves when the root has expanded to extent-tree form.
- Insert, split, merge, and decrement paths are implemented by `ocfs2_insert_refcount_rec()`, `ocfs2_split_refcount_rec()`, `ocfs2_change_refcount_rec()`, `__ocfs2_increase_refcount()`, and `__ocfs2_decrease_refcount()`.
- Full leaves trigger `ocfs2_expand_refcount_tree()`, which either converts an inline root into a leaf-backed btree or splits an existing leaf with `ocfs2_new_leaf_refcount_block()`.
- Empty leaf refcount blocks are removed from the refcount extent tree and queued for delayed block deallocation.
- `ocfs2_calc_refcount_meta_credits()` predicts journal credits and metadata reservations needed for refcount edits and possible tree expansion.

COW behavior:
- `ocfs2_refcount_cal_cow_clusters()` chooses the COW range, preferring up to `MAX_CONTIG_BYTES` chunks to avoid excessive fragmentation.
- `ocfs2_lock_refcount_allocators()` reserves metadata and optional data clusters based on data extent-tree and refcount-tree needs.
- `ocfs2_make_clusters_writable()` either clears the refcount flag when the refcount is one or allocates replacement clusters, duplicates data, updates the data extent tree, and decrements old refcounts.
- Data duplication uses page-cache based copying for file data via `ocfs2_duplicate_clusters_by_page()` and journaled block copying for xattrs via `ocfs2_duplicate_clusters_by_jbd()`.
- `ocfs2_refcount_cow()` repeatedly COWs refcounted file extents until the requested write range is safe to modify.
- `ocfs2_refcount_cow_xattr()` applies the same mechanism to xattr value roots with a post-refcount callback hook.

Reflink behavior:
- `ocfs2_attach_refcount_tree()` ensures the source inode has a refcount tree and marks all existing data/xattr extents refcounted.
- `ocfs2_add_refcount_flag()` marks a data extent refcounted and inserts/increments the corresponding refcount record in one transaction.
- `ocfs2_create_reflink_node()` attaches the target inode to the source tree, duplicates inline data or extent lists, and increments shared refcounts.
- `ocfs2_reflink()` creates a temporary orphan inode, locks the source, builds the reflink target, copies xattrs, completes inode metadata, then moves the orphan into the destination directory.
- `ocfs2_reflink_ioctl()` implements the legacy OCFS2 reflink ioctl path with path lookup, permission checks, and same-mount validation.
- `ocfs2_reflink_remap_blocks()` supports range remapping between files, ensuring both inodes share one refcount tree, punching destination ranges, mapping shared extents, and updating refcounts.
- `ocfs2_reflink_inodes_lock()` / `ocfs2_reflink_inodes_unlock()` provide ordered double-inode locking for reflink/remap callers.

Concurrency and dependencies:
- Uses OCFS2 DLM refcount locks, local rwsem `rf_sem`, metadata cache locking, inode cluster locks, VFS inode locks, `ip_alloc_sem`, `ip_xattr_sem`, and ordered double locking.
- All on-disk refcount, extent, dinode, and xattr changes are journaled with explicit credit calculation and metadata allocator reservations.
- Depends heavily on OCFS2 extent-tree helpers, suballocators, truncate-log/deferred deallocation, xattrs, quota accounting, page cache, writeback, inode security, namei, and symlink helpers.

Risks and edge cases:
- Refcount root block reuse is guarded by generation checks; missing this would make locks protect stale metadata.
- The split logic depends on 64-bit record ordering while btree indexing uses low 32-bit positions, so split positions must avoid low-cpos overlap.
- COW must invalidate extent maps after attempted replacement because both success and partial failure can make cached mappings stale.
- Reflink does not merge different refcount trees between source and destination; that case returns `-EOPNOTSUPP`.
- Crashes or transaction-credit miscalculation during COW/reflink could desynchronize data extent flags, refcount records, and quota accounting.
