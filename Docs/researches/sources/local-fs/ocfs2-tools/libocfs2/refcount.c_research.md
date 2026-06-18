# File Research: sources/local-fs/ocfs2-tools/libocfs2/refcount.c

Implements OCFS2 refcount trees and copy-on-write handling for reflinked file and xattr data.

Core structures:
- `ocfs2_refcount_block` can be an inline root holding refcount records or a tree root holding an extent list of leaf refcount blocks.
- Leaf records are `ocfs2_refcount_rec` entries with physical cluster position, cluster length, and refcount.
- `ocfs2_cow_context` abstracts CoW over normal inode data and xattr value data, carrying an extent tree, refcount root buffer, target range, cluster lookup callback, and optional post-refcount callback.

Endian and block I/O:
- Swap helpers cover refcount lists, refcount records, refcount block headers, and either extent-list or record-list payload depending on `OCFS2_REFCOUNT_TREE_FL`.
- `ocfs2_read_refcount_block_nocheck()` validates block number, reads the block, validates metadata ECC, checks `OCFS2_REFCOUNT_BLOCK_SIGNATURE`, copies to caller buffer, and swaps to CPU endian.
- `ocfs2_read_refcount_block()` additionally validates list usage/count bounds.
- `ocfs2_write_refcount_block()` requires RW, swaps to disk endian, computes metadata ECC, writes the block, and marks the filesystem changed.

Record lookup and mutation:
- `ocfs2_get_refcount_rec()` returns the record containing a physical cluster position or a synthetic hole record with refcount 0.
- For tree roots, it finds the leaf extent using low 32 bits of the physical cpos, reads the refcount leaf, and searches its record list.
- Record contiguity helpers merge adjacent records with equal refcount.
- `ocfs2_change_refcount_rec()` increments/decrements a record, removes it if count reaches zero, optionally merges, and writes the leaf.
- `ocfs2_insert_refcount_rec()` inserts a new record, expanding the tree if the leaf is full.
- `ocfs2_split_refcount_rec()` splits an existing record around a subrange for partial increments, decrements, or hole punching.

Tree growth and shrinking:
- `ocfs2_expand_inline_ref_root()` converts an inline root into a tree root by allocating a new leaf block and moving existing records there.
- `ocfs2_divide_leaf_refcount_block()` sorts records by low 32-bit cpos, finds a split point that avoids overlapping low-cpos ranges, moves half to a new block, then restores 64-bit order.
- `ocfs2_new_leaf_refcount_block()` allocates and inserts a new leaf into the refcount extent tree.
- `ocfs2_expand_refcount_tree()` handles inline-root expansion and then leaf splitting.
- `ocfs2_adjust_refcount_rec()` updates the extent record cpos when a leaf’s first record changes.
- `ocfs2_remove_refcount_extent()` removes an empty leaf from the tree, deletes its block, decrements root cluster count, and restores inline-root style if no leaves remain.

Public refcount operations:
- `ocfs2_increase_refcount()` reads an inode’s refcount root and increments refcounts over a physical range.
- `ocfs2_decrease_refcount()` decrements records and optionally frees physical clusters when the old refcount was 1 and deletion is requested.
- `ocfs2_refcount_punch_hole()` removes all refcount records over a physical range, decrementing by their full current count.
- `ocfs2_change_refcount()` sets a range to a target refcount by computing a delta and applying the increase path.
- `ocfs2_refcount_tree_get_rec()` maps a physical cpos to the refcount tree extent record covering it.
- `ocfs2_create_refcount_tree()` creates a new refcount tree with random generation from `/dev/urandom`.
- `ocfs2_attach_refcount_tree()` increments tree `rf_count`, then sets inode `i_refcount_loc` and `OCFS2_HAS_REFCOUNT_FL`.
- `ocfs2_detach_refcount_tree()` decrements `rf_count`, deletes the tree if it reaches zero, then clears inode refcount fields.

CoW for file data:
- `ocfs2_refcount_cal_cow_clusters()` chooses the virtual cluster range to CoW, aligning splits to up to 1 MiB (`MAX_CONTIG_BYTES`) for better extent layout while not passing holes, unrefcounted extents, or `max_cpos`.
- `ocfs2_duplicate_clusters()` copies physical cluster contents block-by-block.
- `ocfs2_make_clusters_writable()` walks refcount records: if refcount is 1, it just clears the extent refcount flag; if greater than 1, it allocates replacement clusters, copies data unless unwritten, updates the file extent to the new clusters and clears `OCFS2_EXT_REFCOUNTED`, then decrements old refcounts.
- `ocfs2_refcount_cow()` iterates file extents in a write range and CoWs refcounted hunks before writing the cached inode.

CoW and flag changes for xattrs:
- `ocfs2_change_refcount_flag()` changes refcount flags on either inode data extents or xattr value extents, locating xattr extents by physical cluster.
- `ocfs2_refcount_cow_xattr()` performs the same CoW process for xattr value roots. If the xattr extent root lives in a bucket, it uses a post-refcount callback to write the whole bucket.

Important invariants:
- Most public operations assert the inode has `OCFS2_HAS_REFCOUNT_FL` and a valid `i_refcount_loc`.
- Refcount records are expected sorted by 64-bit `r_cpos` in leaves, while tree indexing uses low 32 bits.
- CoW requires the filesystem-level refcount feature; otherwise `ocfs2_replace_cow()` returns read-only filesystem error.
- Error paths often prioritize on-disk recoverability by writing old/new refcount blocks in ordered steps and relying on fsck to repair partially completed splits.
