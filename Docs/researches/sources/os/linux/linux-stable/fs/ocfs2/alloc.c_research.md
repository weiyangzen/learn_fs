# File Research: sources/os/linux/linux-stable/fs/ocfs2/alloc.c

Purpose: implements OCFS2 extent allocation, extent b-tree mutation, truncate-log handling, delayed deallocation, inline-data conversion, truncate zeroing, and filesystem trim support. The file is the central allocator/mutator for extent trees stored in dinodes, xattr value roots, xattr tree roots, directory index roots, and refcount blocks.

Read coverage: complete file read, 7741 lines.

Key structures and state:
- `struct ocfs2_extent_tree_operations` abstracts root-specific extent-tree behavior: last extent block pointer, cluster count updates, extent-map updates, insert checks, root extent-list discovery, optional max leaf size, and custom contiguity rules.
- `struct ocfs2_extent_tree` instances are initialized for dinodes, xattr trees, xattr values, dx roots, and refcount trees. Dinode trees update `i_clusters` and in-memory `ip_clusters`; xattr/dx/refcount trees update their own on-disk cluster counters.
- `struct ocfs2_path` represents a root-to-leaf traversal through an extent b-tree and owns buffer-head references for each level.
- Internal insert state uses `ocfs2_insert_type`, `ocfs2_append_type`, `ocfs2_split_type`, and `ocfs2_merge_ctxt` to decide whether operations are append, contiguous merge, split, rotation, or tree growth.
- Delayed frees are tracked with `ocfs2_cached_block_free`, `ocfs2_per_slot_free_list`, and `ocfs2_cached_dealloc_ctxt`, separating block-suballocator frees from global cluster frees.

Major logic:
- Extent-tree initialization installs root buffer, caching info, journal-access function, root object, root extent list, and optional leaf cluster limit.
- Path helpers allocate, clone, move, reset, journal, and free `ocfs2_path` objects. Search helpers traverse interior records by logical cluster position and can return a full path or just the target leaf.
- Extent block reads validate metadata ECC, signature, block number, filesystem generation, record count, and `l_next_free_rec` before use.
- Metadata growth allocates or reuses extent blocks, initializes extent-block headers, shifts root depth, adds branches, links rightmost leaves, and maintains `last_eb_blk`.
- Insert logic detects contiguous records, tail appends, free record availability, and required rotations. If no record is available, it grows the tree; otherwise it inserts, appends, coalesces, or rotates records into leaf space.
- Right rotations create an empty extent slot for insertion. Left rotations remove empty slots, rebalance neighboring leaves, and may unlink empty rightmost paths.
- Split and merge logic handles left, right, and middle splits, including cross-extent-block merges. It tries to merge with adjacent compatible records before growing the tree.
- Extent flag changes, including marking unwritten extents written, are implemented by splitting/replacing/merging target extent records.
- Range removal truncates, splits, or deletes extent records, updates edge lengths, updates cluster accounting, handles refcounted extents, appends non-refcounted frees to the truncate log, and defers metadata block frees.
- The truncate log batches freed clusters in per-slot system inodes. It supports append/coalesce, flush/replay, delayed work scheduling, allocation retry after flush, mount-time initialization, shutdown flush, and node recovery handoff.
- Delayed deallocation groups metadata-block frees by system inode type and slot, frees them after higher-level operations drop sensitive locks, and can reuse recently deleted extent blocks during tree growth.
- Folio helpers map, zero, dirty, mark uptodate, and order data writes for partial cluster truncation and inline-data conversion.
- Inline-data helpers initialize dinode extent lists, switch dinodes into inline-data format, and convert inline file data to a one-cluster extent while preserving quota, folio, and rollback behavior.
- `ocfs2_commit_truncate()` repeatedly walks the rightmost extent path, removes full or partial tail records, handles refcounted extents, schedules truncate-log flushing, and runs delayed deallocations.
- `ocfs2_trim_fs()` coordinates cluster-wide fstrim with a trim lock, avoids duplicate trims already completed by another node, scans the global bitmap group by group, and issues discard for sufficiently large free runs.

Important entry points:
- Extent-tree setup: `ocfs2_init_dinode_extent_tree()`, `ocfs2_init_xattr_tree_extent_tree()`, `ocfs2_init_xattr_value_extent_tree()`, `ocfs2_init_dx_root_extent_tree()`, `ocfs2_init_refcount_extent_tree()`.
- Tree/path utilities: `ocfs2_read_extent_block()`, `ocfs2_num_free_extents()`, `ocfs2_find_path()`, `ocfs2_find_leaf()`, `ocfs2_search_extent_list()`.
- Allocation and mutation: `ocfs2_insert_extent()`, `ocfs2_add_clusters_in_btree()`, `ocfs2_split_extent()`, `ocfs2_change_extent_flag()`, `ocfs2_mark_extent_written()`, `ocfs2_remove_extent()`, `ocfs2_remove_btree_range()`.
- Truncate and deallocation: `ocfs2_truncate_log_append()`, `ocfs2_flush_truncate_log()`, `ocfs2_begin_truncate_log_recovery()`, `ocfs2_complete_truncate_log_recovery()`, `ocfs2_run_deallocs()`, `ocfs2_commit_truncate()`.
- Data-shape transitions and cleanup: `ocfs2_zero_range_for_truncate()`, `ocfs2_convert_inline_data_to_extents()`, `ocfs2_truncate_inline()`, `ocfs2_trim_fs()`.

Concurrency and lifetime:
- Extent tree mutation is journaled explicitly; callers must hold the correct inode, metadata, allocator, and cluster locks before entering exported mutation paths.
- Buffer-head ownership is reference-counted through path construction, copy/move, and cleanup. New metadata buffers are journaled as create-access buffers before initialization is dirtied.
- Tree rotations dynamically extend journal credits to cover both the immediate operation and required parent/neighbor updates.
- Dinode cluster counts update both on-disk fields and in-memory inode state under `ip_lock`.
- Truncate-log operations serialize on `osb_tl_inode`’s inode mutex and flush the JBD2 journal before replaying truncate records to avoid crash-replay double frees.
- Refcounted extent removal may acquire the refcount tree lock unless the caller already holds it.
- Folio zeroing locks folios during mapping/dirtying and starts writeback for partial truncation ranges.
- Fstrim uses OCFS2 trim lock resources so concurrent cluster nodes do not issue duplicate discard for the same range.

Important dependencies:
- Relies on OCFS2 journaling, suballocator, local alloc, truncate log, extent map, refcount tree, xattr, inode, and metadata-cache APIs.
- Uses JBD2 transaction credit accounting and journal flush primitives.
- Uses quota accounting for allocated/freed data clusters.
- Uses Linux folio/page-buffer APIs for partial cluster zeroing and inline-data migration.
- Uses block-layer discard via `sb_issue_discard()` for trim.

Risk and edge cases:
- Extent tree invariants are strict: invalid tree depth, empty interior lists, bad block pointers, bad extent-block metadata, and lost records generally become filesystem errors or BUG checks.
- Empty extent records are legal only in tightly controlled leaf positions, usually index 0, and rotation code depends on that invariant.
- Left-contiguous insertion at the first record of a leaf is deliberately downgraded to a non-contiguous path because parent edge updates are complex.
- Cross-leaf merge/split operations require careful journal credit extension and parent record repair; stale paths are reinitialized after tree reshaping.
- `last_eb_blk`, rightmost parent ranges, and `h_next_leaf_blk` must remain synchronized or later appends/truncates can target the wrong edge.
- Truncate-log append and flush are separate transactions, so flush forces a journal checkpoint boundary before replay to prevent double freeing clusters after crash recovery.
- Delayed deallocation reduces lock-ordering risk, but callers must eventually run `ocfs2_run_deallocs()` or cached frees will not reach allocators.
- Inline-data conversion has a narrow late-failure window after data has been moved into page cache and the dinode has been converted; the code compensates with quota and cluster rollback where possible.
- Trim intentionally releases and reacquires bitmap locks between groups to avoid starving other I/O, so progress is group-by-group rather than one long lock hold.
