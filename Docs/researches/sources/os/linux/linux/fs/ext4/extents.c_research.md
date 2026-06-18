# File Research: sources/os/linux/linux/fs/ext4/extents.c

## Purpose

`extents.c` is the main ext4 extent-tree implementation. It owns on-disk extent tree validation, traversal, insertion, split/merge/growth, removal, logical-to-physical mapping, unwritten extent conversion, fallocate range operations, fiemap integration, cluster mapping queries, extent swapping, and fast-commit replay helpers.

The file is tightly coupled to journaling (`jbd2` via `ext4_jbd2.h`), ext4 allocation (`ext4_mb_new_blocks`, `ext4_new_meta_blocks`, `ext4_free_blocks`), extent status cache APIs from `extents_status.c`, iomap fiemap reporting, quota accounting, page-cache invalidation, and fast commit recovery.

## Major Data And State

- On-disk extent tree nodes are represented by `struct ext4_extent_header`, `struct ext4_extent`, `struct ext4_extent_idx`, and `struct ext4_ext_path`.
- `EXT4_I(inode)->i_data` stores the root extent header and root extents/indexes for shallow trees.
- External extent blocks are buffer heads referenced by `path[i].p_bh`.
- `i_data_sem` protects extent tree structure and must be held for most tree mutations; `ext4_datasem_ensure_credits()` may temporarily drop and reacquire it while restarting/extending a journal transaction.
- Metadata checksums are maintained for external extent blocks when `metadata_csum` is enabled.
- The in-memory extent status tree is updated through `ext4_es_cache_extent()`, `ext4_es_insert_extent()`, and `ext4_es_remove_extent()` to keep lookup, delayed allocation, hole, and unwritten state coherent.

## Tree Validation And Access

- `ext4_extent_block_csum()`, `ext4_extent_block_csum_verify()`, and `ext4_extent_block_csum_set()` compute and maintain extent block checksums over the extent block payload up to the tail.
- `ext4_valid_extent()` rejects zero-length/logical-overflow extents and validates physical block ranges through `ext4_inode_block_valid()`.
- `ext4_valid_extent_idx()` validates an index block pointer.
- `ext4_valid_extent_entries()` checks sorted, non-overlapping leaf extents or index entries and verifies child-first logical block consistency against the parent index.
- `__ext4_ext_check()` validates magic, depth, max entries, entry count, non-empty internal nodes, entries, maximum depth, and non-root checksum. It reports corruption via `ext4_error_inode_err()`.
- `ext4_ext_check_inode()` validates an inode root extent header.
- `ext4_ext_get_access()` obtains journal write access for external extent blocks and clears the buffer verified bit before mutation.
- `__ext4_ext_dirty()` sets checksums and dirties either the external metadata buffer or the inode root; successful buffer dirties set `buffer_verified`.

## Path And Traversal Helpers

- `ext4_ext_path_brelse()`, `ext4_ext_drop_refs()`, and `ext4_free_ext_path()` release buffer references held in extent paths.
- `ext4_ext_find_goal()` derives an allocation goal from the current path extent, the current extent block, or the inode locality goal.
- `ext4_ext_new_meta_block()` allocates metadata blocks for tree growth/splits.
- `ext4_ext_space_block()`, `ext4_ext_space_block_idx()`, `ext4_ext_space_root()`, and `ext4_ext_space_root_idx()` compute capacity for leaf/index blocks and inline root storage.
- `ext4_ext_max_entries()` selects the correct capacity for the given depth and root/non-root node.
- `ext4_ext_binsearch_idx()` and `ext4_ext_binsearch()` search sorted index and leaf entries.
- `ext4_ext_tree_init()` initializes a new extent root inside the inode.
- `ext4_find_extent()` is the central lookup routine. It validates root depth, allocates/reuses a path, optionally caches root extents, walks index blocks with `read_extent_tree_block()`, validates loaded nodes, and returns the closest leaf extent for a logical block.
- `__read_extent_tree_block()` reads an extent block, verifies it unless already verified, optionally forces cache population, and caches leaf entries into the extent status tree.
- `ext4_ext_precache()` walks all leaf blocks of an extent-mapped inode and populates the extent status tree; it marks `EXT4_STATE_EXT_PRECACHED`.

## Extent Insertion, Splitting, Growth, And Merge

- `ext4_ext_insert_index()` inserts an index entry into an index block, shifting existing entries and journaling the update.
- `ext4_ext_split()` splits a full path at a selected level, allocates new leaf/index blocks, moves right-side entries into the new subtree, updates checksums, and inserts the new index into the parent. Error cleanup frees newly allocated metadata blocks.
- `ext4_ext_grow_indepth()` grows the tree by one level by moving the current root contents to a new external block and replacing the root with a single index.
- `ext4_ext_create_new_leaf()` finds an index node with free space or grows the tree and then splits until a leaf with space is available.
- `ext4_can_extents_be_merged()` requires matching initialized/unwritten state, adjacent logical ranges, adjacent physical blocks, and length limits (`EXT_INIT_MAX_LEN` / `EXT_UNWRITTEN_MAX_LEN`).
- `ext4_ext_try_to_merge_right()`, `ext4_ext_try_to_merge_up()`, and `ext4_ext_try_to_merge()` merge adjacent extents and, where possible, collapse a one-leaf tree back into the inode root.
- `ext4_ext_check_overlap()` clips a new extent so it does not overlap the next allocated extent or wrap logical block space.
- `ext4_ext_insert_extent()` handles insertion into an existing leaf, append/prepend merge fast paths, next-leaf space reuse, leaf creation, index correction, and final dirtying. It honors flags such as `EXT4_GET_BLOCKS_SPLIT_NOMERGE`, delayed-allocation reservation, and metadata nofail allocation.
- `ext4_split_extent_at()` splits one extent at a logical block while preserving written/unwritten state. On insert failure it restores the original extent length and removes stale ES cache coverage for the affected extent.
- `ext4_split_extent()` can split around a requested map range into up to three extents; if splitting fails due to space/quota/memory and zeroout is allowed, it may zero portions and convert instead.
- `ext4_split_convert_extents()` wraps splitting plus conversion to initialized or unwritten state, updates the ES tree unless `EXT4_EX_NOCACHE` is used, and prevents immediate remerge when requested.

## Removal, Truncate, Punch, And Partial Clusters

- `ext4_ext_search_left()` and `ext4_ext_search_right()` find neighboring allocated blocks for allocation goals, hole detection, and cluster decisions.
- `ext4_ext_next_allocated_block()` and `ext4_ext_next_leaf_block()` find next allocated logical ranges from the current path.
- `ext4_ext_correct_indexes()` updates parent index logical borders when the first extent in a leaf changes; on error it clears verified bits on modified buffers.
- `get_default_free_blocks_flags()` chooses free flags based on inode type and journaling mode.
- `ext4_rereserve_cluster()` restores reserved cluster accounting when freeing a cluster that still has a pending reservation in bigalloc mode.
- `ext4_remove_blocks()` frees data blocks from the tail of an extent, carefully handling first/last partial clusters, pending reservations, bigalloc cluster accounting, and delayed quota behavior.
- `ext4_ext_rm_leaf()` removes whole or tail portions of extents in one leaf, updates extent lengths, shifts entries on hole-punch removals, corrects indexes, frees partial clusters when safe, and removes empty leaf index entries.
- `ext4_ext_rm_idx()` removes an index entry, frees the referenced extent metadata block, and updates parent border keys.
- `ext4_ext_more_to_rm()` guides right-to-left removal traversal.
- `ext4_ext_remove_space()` is the main extent removal engine for truncate and punch. It may split the right edge first, traverses from right to left, removes leaf contents and empty index blocks, handles journal credit restarts through `ext4_datasem_ensure_credits()`, and collapses an empty tree back to depth 0.
- `ext4_ext_truncate()` updates `i_disksize`, removes ES entries past the new EOF, and calls `ext4_ext_remove_space()` with retry on `-ENOMEM`.

## Block Mapping And Allocation

- `ext4_ext_find_hole()` determines a hole around a logical block using the current extent path.
- `ext4_ext_determine_insert_hole()` refines an on-disk hole against delayed extents in the ES tree, caches true holes, and returns the hole length visible from the queried block.
- `get_implied_cluster_alloc()` handles bigalloc cluster sharing cases where a hole inside an already allocated physical cluster should map to the cluster instead of allocating a new one.
- `ext4_ext_map_blocks()` is the central extent-backed map/allocation path:
  - Looks up the nearest extent through `ext4_find_extent()`.
  - Returns initialized mappings directly.
  - Handles initialized-to-unwritten conversion when requested.
  - Delegates unwritten extent conversion or lookup handling to `ext4_ext_handle_unwritten_extents()`.
  - Returns holes for non-create lookups and caches hole status through ES.
  - For create requests, computes neighbors, bigalloc implied allocation, extent length limits, overlap clipping, allocation goals, allocation flags, and calls `ext4_mb_new_blocks()`.
  - Inserts the newly allocated extent and frees allocated clusters on recoverable insertion failures.
  - Sets `EXT4_MAP_NEW`, `EXT4_MAP_MAPPED`, and `EXT4_MAP_UNWRITTEN` flags as appropriate.
- `ext4_ext_calc_credits_for_single_extent()` and `ext4_ext_index_trans_blocks()` estimate journal credits for insertions and possible tree splits.
- `ext4_ext_zeroout()` issues zeroing for a physical extent range; `ext4_zeroout_es()` updates ES state after successful zeroout paths.

## Unwritten Extent Conversion

- `ext4_ext_convert_to_initialized()` converts unwritten extents for buffered writes. It has fast paths that transfer blocks into initialized left/right neighbors within the same leaf, and fallback split/zeroout logic for head, tail, or middle writes.
- `ext4_ext_handle_unwritten_extents()` handles IO completion conversion, fallocate repeat requests, read/write lookup of unwritten extents, and buffered write conversion. It forces metadata nofail behavior for writes into unwritten space.
- `ext4_convert_unwritten_extents_endio()` converts a completed unwritten IO range to initialized.
- `convert_initialized_extent()` converts initialized extents to unwritten, used by zero-range/write-zeroes style operations.
- `ext4_convert_unwritten_extents_atomic()` converts atomic-write ranges within a single transaction when possible and logs when split mappings are discovered.
- `ext4_convert_unwritten_extents()` converts normal DIO/fallocate unwritten ranges, explicitly using `EXT4_EX_NOCACHE` because it does not hold all locks needed to safely cache unrelated extents.
- `ext4_convert_unwritten_io_end_vec()` converts all io-end vectors, optionally using a reserved journal handle.

## Fallocate And Range Operations

- `ext4_alloc_file_blocks()` loops over `ext4_map_blocks()` to allocate unwritten or zeroed ranges, manages journal transactions, handles retries on ENOSPC, optionally zeroes and converts allocated unwritten extents, and updates file size for successful partial progress.
- `ext4_zero_range()` implements zero range and write-zeroes. It preallocates unaligned edges, updates disk size before punch-like invalidation, drops page cache, converts aligned interior blocks to unwritten or written-zero blocks, zeroes partial blocks, and syncs when needed.
- `ext4_do_fallocate()` implements normal preallocation with unwritten extents and handles sync fast-commit commit behavior.
- `ext4_fallocate()` validates mode combinations, rejects encrypted collapse/insert and unsupported write-zeroes, converts inline data, waits for DIO, marks file modification, locks invalidation for page-cache-dropping modes, and dispatches punch, collapse, insert, zero, or allocate operations.
- `ext4_ext_shift_path_extents()` shifts a leaf segment and required parent index borders left or right, merging as it goes and restarting transaction credits when needed.
- `ext4_ext_shift_extents()` shifts all extents in a range left or right, validating hole/EOF constraints and iterating across leaves.
- `ext4_collapse_range()` removes a cluster-aligned middle range, invalidates page cache, removes the target extents, shifts following extents left, updates size/disksize, and marks the operation fast-commit-ineligible.
- `ext4_insert_range()` expands size first, splits an extent at the insertion point if needed, drops ES cache from the insertion point onward, shifts following extents right, and marks fast-commit ineligible.

## Fiemap, ES Cache Reporting, And Xattrs

- `ext4_fill_es_cache_info()` walks ES cache entries and emits fiemap records for written, unwritten, delayed, and hole extents.
- `ext4_iomap_xattr_fiemap()` reports in-inode or external extended attribute storage via iomap, returning `-ENOENT` when no xattr storage exists.
- `ext4_fiemap_check_ranges()` validates and clips fiemap ranges against ext4 max bytes.
- `ext4_fiemap()` handles `FIEMAP_FLAG_CACHE`, range validation, xattr fiemap dispatch, and normal iomap fiemap dispatch.
- `ext4_get_es_cache()` exposes ES-cache-backed fiemap-like information after optional precache and range preparation.

## Swap, Bigalloc Queries, And Fast Commit Replay

- `ext4_swap_extents()` swaps physical block pointers between two inodes over a range. It assumes both inode locks and both `i_data_sem` locks are held, removes ES cache coverage first, splits both sides to align boundaries, swaps pblocks and unwritten state, merges neighbors, and dirties both leaves.
- `ext4_clu_mapped()` determines whether any block in a logical cluster is mapped, used by bigalloc reservation logic.
- `ext4_ext_replay_update_ex()` updates an extent during fast-commit replay by splitting to exact boundaries if needed, setting written/unwritten state and physical block, dirtying the leaf without a normal handle, and marking the inode dirty.
- `ext4_ext_replay_shrink_inode()` walks replayed extents and attempts to merge them.
- `skip_hole()` advances a logical cursor over holes using `ext4_map_blocks()`.
- `ext4_ext_replay_set_iblocks()` recomputes `i_blocks` after replay by counting mapped data blocks and extent tree metadata blocks.
- `ext4_ext_clear_bb()` marks replayed extent metadata/data blocks in block bitmaps and records fast-commit regions.

## Initialization And Test Hooks

- `ext4_ext_init()` and `ext4_ext_release()` initialize/report optional extent debug statistics.
- KUnit-only exports expose `ext4_ext_space_root_idx_test()`, `ext4_split_convert_extents_test()`, `__ext4_ext_dirty`, `ext4_ext_zeroout`, ES shrinker helpers, ES lookup/insert/init helpers, `ext4_ext_insert_extent()`, `ext4_find_extent()`, `ext4_issue_zeroout()`, and map query/create helpers for ext4 tests.

## Locking And Consistency Notes

- Tree modifications assume `i_data_sem` write locking; lookup-only callers use read locking unless allocation/conversion is possible.
- Removal paths may drop `i_data_sem` while restarting journal credits through `ext4_datasem_ensure_credits()`, relying on higher-level exclusion for truncate/punch workflows.
- Range operations that drop page cache hold `i_rwsem` and `invalidate_lock` at higher levels to prevent page faults and writeback races.
- `EXT4_EX_NOCACHE` is used during in-progress tree modifications and some IO-completion conversions to avoid polluting or corrupting ES state with unstable mappings.
- Parent index border maintenance is critical when first extents in leaves shift, split, or are removed.
- Bigalloc paths have extra partial-cluster and pending-reservation handling to avoid freeing shared clusters or losing delayed allocation reservations.

## Failure And Risk Areas

- Extent splitting has complex rollback behavior: insertion failures restore original length and clear ES coverage, but non-recoverable corruption paths intentionally avoid freeing potentially leaked blocks if doing so could worsen damage.
- `ext4_datasem_ensure_credits()` can drop `i_data_sem`; callers that mutate broad ranges need external locks and page-cache invalidation to keep ES and on-disk trees coherent.
- Unwritten conversion has several zeroout fallback paths; correctness depends on extent ranges remaining unchanged between failed split and fallback validation.
- Range shifting mutates logical keys across leaves and parents; off-by-one errors can corrupt tree ordering, so alignment and boundary checks are strict.
- Fast-commit replay helpers operate without normal transaction handles and intentionally dirty metadata/inodes in replay context; they depend on replay-time invariants.
