# File Research: sources/os/linux/linux/fs/ocfs2/alloc.h

## Purpose

`alloc.h` is the public interface for OCFS2 allocation and extent-tree manipulation implemented mostly by `alloc.c`. It declares the generic extent-tree abstraction, path abstraction, truncate-log API, cached deallocation API, inline-data conversion/truncation helpers, b-tree search helpers, and fstrim entry point used by other OCFS2 files.

## Extent Tree Interface

The header declares `struct ocfs2_extent_tree`, the caller-visible object that represents any OCFS2 extent b-tree root. It contains:

- private operation table pointer `et_ops`;
- root buffer head `et_root_bh`;
- root extent list `et_root_el`;
- caching info `et_ci`;
- root journal access callback `et_root_journal_access`;
- root object pointer `et_object`;
- optional `et_max_leaf_clusters` limit;
- optional cached deallocation context `et_dealloc`.

The header documents that callers must initialize this structure with one of the provided initializers before using the allocation code:

- `ocfs2_init_dinode_extent_tree`;
- `ocfs2_init_xattr_tree_extent_tree`;
- `ocfs2_init_xattr_value_extent_tree`;
- `ocfs2_init_dx_root_extent_tree`;
- `ocfs2_init_refcount_extent_tree`.

This allows `alloc.c` to operate generically on dinode data, xattr data, xattr tree blocks, indexed directory roots, and refcount trees while preserving owner-specific cluster counters, journaling, and last-leaf fields.

`OCFS2_MAX_XATTR_TREE_LEAF_SIZE` is defined as 65536 bytes and is used by xattr tree extent handling to cap leaf extent size.

## Core Extent Operations

The header exports the primary b-tree operations:

- `ocfs2_read_extent_block`: cached and validated read of an extent block.
- `ocfs2_insert_extent`: insert a logical-to-physical extent record into an initialized extent tree.
- `ocfs2_add_clusters_in_btree`: claim clusters and insert them into an extent tree, with restart reporting.
- `ocfs2_split_extent`: split or replace a leaf extent record and merge adjacent compatible records.
- `ocfs2_mark_extent_written`: convert unwritten extents to written extents over a range.
- `ocfs2_change_extent_flag`: set/clear extent flags over a range.
- `ocfs2_remove_extent`: remove a logical extent range from a tree.
- `ocfs2_remove_btree_range`: high-level removal path that also handles quota, truncate log, refcount trees, and cached deallocation.
- `ocfs2_num_free_extents`: count free records in the relevant leaf for future metadata planning.

`enum ocfs2_alloc_restarted` communicates why `ocfs2_add_clusters_in_btree` returned a restart condition:

- `RESTART_NONE`;
- `RESTART_TRANS`;
- `RESTART_META`.

`ocfs2_extend_meta_needed` is an inline conservative estimator for the maximum number of new metadata blocks needed by an allocation. It returns `root_el->l_tree_depth + 2`, covering a block per current level, one new depth-zero extent block, and one new top-level block. The comment explicitly requires `root_el` to be the actual root list.

## Dinode, Inline Data, And Truncate Helpers

The header exports helpers for changing dinode storage format:

- `ocfs2_dinode_new_extent_list`: initialize a dinode as an empty extent-list owner.
- `ocfs2_set_inode_data_inline`: initialize inline-data storage in a dinode.
- `ocfs2_convert_inline_data_to_extents`: move inline file data into a real allocated extent.

Truncation-related exports include:

- `ocfs2_zero_range_for_truncate`: zero partial clusters before truncate/hole punch.
- `ocfs2_commit_truncate`: remove extents after inode size has been adjusted.
- `ocfs2_truncate_inline`: zero/truncate inline data.

`struct ocfs2_truncate_context` combines a cached deallocation context with truncate-specific state, including whether the extent allocator is locked and the last extent block buffer. The header notes that parts of it are destroyed once passed to commit-truncate logic.

## Truncate Log API

The header exposes the truncate-log lifecycle and recovery interface:

- `ocfs2_truncate_log_init`;
- `ocfs2_truncate_log_shutdown`;
- `ocfs2_schedule_truncate_log_flush`;
- `ocfs2_flush_truncate_log`;
- `__ocfs2_flush_truncate_log`;
- `ocfs2_begin_truncate_log_recovery`;
- `ocfs2_complete_truncate_log_recovery`;
- `ocfs2_truncate_log_needs_flush`;
- `ocfs2_truncate_log_append`;
- `ocfs2_try_to_free_truncate_log`.

These functions let other OCFS2 code append freed cluster ranges, flush local truncate logs, recover another slot's truncate log during node recovery, and opportunistically flush logs to satisfy allocation pressure.

## Cached Deallocation API

`struct ocfs2_cached_dealloc_ctxt` stores delayed frees:

- `c_first_suballocator`: grouped block frees by system inode type and slot;
- `c_global_allocator`: cluster frees destined for the global allocator/truncate log.

The inline initializer `ocfs2_init_dealloc_ctxt` clears both lists. Exported helpers:

- `ocfs2_cache_cluster_dealloc`: queue cluster-range deallocation;
- `ocfs2_cache_block_dealloc`: queue suballocator block deallocation;
- `ocfs2_dealloc_has_cluster`: test whether cluster frees are queued;
- `ocfs2_run_deallocs`: execute all cached frees later, outside sensitive lock scopes.

The comments explain the intended usage: allocation-tree routines may cache block unlinks locally, and callers should call `ocfs2_run_deallocs` after deallocating routines complete, without open journal handles and after most locks are dropped.

## Extent Record Helpers

The header provides two important inline helpers:

- `ocfs2_rec_clusters`: returns the record cluster count using `e_int_clusters` for interior nodes and `e_leaf_clusters` for leaves. This hides the on-disk format difference caused by leaf extent flags.
- `ocfs2_is_empty_extent`: true when a leaf record has zero `e_leaf_clusters`; the comment notes this is only valid for leaf nodes.

It also declares `ocfs2_search_extent_list`, which finds the record containing a logical cluster in either interior or leaf lists.

## Path Interface

The header defines:

- `struct ocfs2_path_item`: buffer head plus extent list pointer;
- `OCFS2_MAX_PATH_DEPTH` as 5;
- `struct ocfs2_path`: tree depth, root journal access callback, and fixed node array.

Macros expose root and leaf buffer/list access:

- `path_root_bh`, `path_root_el`, `path_root_access`;
- `path_leaf_bh`, `path_leaf_el`;
- `path_num_items`.

Exported path functions:

- `ocfs2_reinit_path`;
- `ocfs2_free_path`;
- `ocfs2_find_path`;
- `ocfs2_new_path_from_path`;
- `ocfs2_new_path_from_et`;
- `ocfs2_path_bh_journal_access`;
- `ocfs2_journal_access_path`;
- `ocfs2_find_cpos_for_right_leaf`;
- `ocfs2_find_cpos_for_left_leaf`;
- `ocfs2_find_subtree_root`.

These are used by allocation, refcount, xattr, and other OCFS2 subsystems that need to navigate or modify extent b-trees while preserving journaling semantics.

## Folio And Trim Entry Points

`ocfs2_map_and_dirty_folio` maps a folio range to physical blocks, optionally zeroes it, marks buffers dirty/uptodate, and integrates ordered-data journaling. It is declared here because allocation/truncation and inline conversion code need the helper across compilation units.

`ocfs2_trim_fs` is the exported fstrim entry point for OCFS2. Its implementation in `alloc.c` scans the global bitmap and uses cluster-wide trim locking to avoid duplicate discard from multiple nodes.

## Research Notes

This header is the contract for OCFS2's generic extent-tree machinery. Its most important design point is that extent editing is not tied directly to `ocfs2_dinode`; callers provide an initialized `ocfs2_extent_tree`, and `alloc.c` dispatches owner-specific root updates through operations installed by the initializer. Consumers must respect the documented sequencing around journaling, metadata reservation, truncate-log locking, and delayed deallocation.
