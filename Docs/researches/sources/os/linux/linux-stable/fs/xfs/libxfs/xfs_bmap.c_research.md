# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the core XFS logical-to-physical block mapping implementation. It translates file offsets to filesystem blocks, allocates and frees extents, converts delayed allocation and unwritten extents, maintains inode fork extent state, and coordinates bmap updates with reverse mapping, refcount, quota, realtime allocation, deferred operations, and transaction logging.

It handles three mapping domains:

- Data fork mappings for normal file data.
- Attribute fork mappings for extended attribute storage.
- CoW fork mappings for reflink/copy-on-write staging extents, with in-core quota and refcount behavior distinct from data fork mappings.

## Major Responsibilities

- Compute bmap btree maximum levels and default attribute fork offsets.
- Convert inode fork formats between local, extent, and btree representations.
- Load btree-format extents into the in-core extent cache.
- Query first/last mapped or unused logical blocks.
- Add extents for delayed allocation conversion, unwritten conversion, hole allocation, and reflink remap.
- Select and perform block allocations, including stripe alignment, extent size hints, filestream AG selection, low-space fallback, realtime allocation dispatch, and debug minlen injection.
- Map read ranges without allocation via `xfs_bmapi_read`.
- Map write ranges with allocation/conversion via `xfs_bmapi_write`.
- Convert individual delalloc extents for writeback via `xfs_bmapi_convert_delalloc`.
- Unmap ranges via `xfs_bunmapi` and `xfs_bunmapi_range`.
- Shift/split extents for collapse range, insert range, and extent splitting operations.
- Record and finish deferred bmap intent items.
- Validate extent records and expose btree query helpers.
- Initialize and destroy the `xfs_bmap_intent` slab cache.

## Important Data Flow

The file's central state carrier for allocations is `struct xfs_bmalloca`, declared in `xfs_bmap.h`. Allocation callers populate transaction, inode, fork flags, logical offset, length, neighboring extents, and reservation totals. The allocator fills in physical block and final extent state, while helper functions update in-core extent records, btree records, inode counters, delayed block counters, quota, and transaction log flags.

Read-only mapping (`xfs_bmapi_read`) loads extents if necessary, walks the in-core extent tree, synthesizes hole records, trims results to the requested range unless `XFS_BMAPI_ENTIRE` is set, and merges adjacent return records when possible.

Write mapping (`xfs_bmapi_write`) loads extents, walks the requested logical range, allocates holes or delayed extents, optionally converts unwritten extents, returns mappings, and finally converts the fork back from btree to extent format if it has become small enough.

Unmapping (`__xfs_bunmapi`) walks extents backwards over the target range, handles realtime extent alignment constraints, deletes delayed or real extents through dedicated helpers, frees or refcount-decrements blocks unless remapping, and may convert between extent and btree formats after extent count changes.

## Key Functions and Behavior

- `xfs_bmap_compute_maxlevels` calculates mount-time max bmap btree height for data or attr forks based on maximum possible extent count and minimum btree fanout.
- `xfs_bmap_compute_attr_offset` and `xfs_default_attroffset` determine where attr fork space starts inside the inode.
- `xfs_bmap_btree_to_extents` collapses a shallow btree fork back to inline extent format when extent count fits.
- `xfs_bmap_extents_to_btree` allocates a child btree block, builds a root in the inode, copies non-null in-core extents to the leaf, and initializes a btree cursor.
- `xfs_bmap_local_to_extents` converts local-format fork data into a one-block extent using a caller-provided remote block initializer.
- `xfs_bmap_add_attrfork` creates an attr fork and may force the data fork from local/extents into a form that leaves enough inode space.
- `xfs_iread_extents` visits all bmap btree record blocks and materializes validated records into the in-core extent tree.
- `xfs_bmap_add_extent_delay_real` replaces all or part of a delalloc extent with allocated blocks, merging with neighbors when physically and logically contiguous.
- `xfs_bmap_add_extent_unwritten_real` toggles written/unwritten state for all or part of a real extent and merges/splits neighboring extents.
- `xfs_bmap_add_extent_hole_real` inserts a newly allocated extent into a hole and merges with adjacent real extents when possible.
- `xfs_bmap_extsize_align` expands or adjusts allocation offsets and lengths according to extent size hints and realtime extent size constraints.
- `xfs_bmap_btalloc` is the primary data-device allocator wrapper, selecting alignment and allocation strategy before accounting for success.
- `xfs_bmapi_allocate` drives allocation for one logical subrange and dispatches to delayed-real or hole-real extent insertion.
- `xfs_bmapi_remap` installs an existing physical range into an inode fork, used for reflink/deferred bmap map operations.
- `xfs_bmap_del_extent_delay`, `xfs_bmap_del_extent_cow`, and `xfs_bmap_del_extent_real` remove or split extents and perform the appropriate accounting for delayed, CoW, or real mappings.
- `xfs_bmap_collapse_extents`, `xfs_bmap_insert_extents`, and `xfs_bmap_split_extent` support logical file range manipulation by shifting or splitting extent records and updating rmaps.
- `xfs_bmap_finish_one` executes deferred bmap map/unmap intent work.
- `xfs_bmap_validate_extent_raw` and `xfs_bmap_validate_extent` reject invalid file ranges, physical ranges, and unwritten-state combinations for non-data forks.

## Extent State Machine

The add/delete paths use bit flags such as `BMAP_LEFT_FILLING`, `BMAP_RIGHT_FILLING`, `BMAP_LEFT_CONTIG`, and `BMAP_RIGHT_CONTIG` to describe whether the changed subrange touches the left or right edge of an existing extent and whether neighboring extents can be merged. This produces explicit switch cases for:

- Replacing an entire extent and merging both sides.
- Replacing only the left or right edge.
- Replacing a middle segment, splitting one record into three.
- Inserting a hole allocation with no merge, left merge, right merge, or both-side merge.
- Deleting an entire, leading, trailing, or middle part of an extent.

The same broad pattern appears in delayed allocation conversion, unwritten conversion, hole allocation, delayed deletion, CoW deletion, and real deletion, with different accounting and btree update requirements.

## Allocation Strategy

Allocation prefers locality and alignment but falls back aggressively:

- `xfs_bmap_adjacent` chooses a starting block based on adjacent extents for contiguous layout.
- `xfs_bmap_btalloc_select_lengths` scans AG free-space summaries to choose a useful minimum length.
- `xfs_bmap_btalloc_at_eof` tries exact EOF extension before aligned allocation.
- `xfs_bmap_btalloc_filestreams` honors filestream AG selection.
- `xfs_bmap_btalloc_best_length` performs general data-device allocation.
- `xfs_bmap_btalloc_low_space` reduces requests to minimum size and then performs a first-AG full scan, setting `XFS_TRANS_LOWMODE`.
- Realtime files dispatch to `xfs_bmap_rtalloc` outside this file.

Allocation accounting is centralized in `xfs_bmap_alloc_account`, which treats CoW fork allocations as in-core quota reservations until remap, and treats data/attr allocations as real inode block count and quota updates.

## Consistency, Validation, and Recovery Hooks

The implementation is transaction-centric. Any extent mutation updates in-core extent state, optional btree records, inode extent counts, inode block counts, quota counters, reverse mappings, refcount records, and log flags. Deferred free and deferred bmap intent mechanisms preserve ordering between file mapping removal, rmap updates, refcount changes, and block freeing.

Corruption checks use `XFS_IS_CORRUPT`, `xfs_bmap_mark_sick`, `xfs_btree_mark_sick`, verifier errors, and `-EFSCORRUPTED`. Debug builds add expensive leaf-order validation for btree extents and return-map assertions.

## Dependencies

This file depends heavily on:

- In-core extent helpers from the inode fork layer (`xfs_iext_*`).
- Generic btree operations (`xfs_btree_*`) and bmap btree helpers from `xfs_bmap_btree.c`.
- Allocation and AG state (`xfs_alloc_*`, `xfs_perag`, filestream helpers).
- Realtime allocation/freeing (`xfs_rtbitmap`, `xfs_rtgroup`).
- Reverse mapping and refcount subsystems (`xfs_rmap_*`, `xfs_refcount_*`).
- Transaction, deferred operation, quota, and inode logging APIs.
- Iomap conversion helpers for writeback.

## Notable Invariants

- CoW fork never converts to btree format through these helpers.
- Extents must remain sorted by logical offset and non-overlapping.
- Real extents can merge only when logical offsets, physical blocks, state, maximum extent length, and realtime group constraints all permit it.
- Attribute fork and CoW fork cannot store unwritten extents in the same way as data fork; validation rejects invalid state combinations.
- Btree format should collapse back to extents when extent count fits, except for CoW fork.
- Btree block allocations and frees update inode block counts and quota like metadata owned by the inode.

## Research Notes

This is one of the highest-risk XFS files because it is the convergence point for allocation, delayed allocation, reflink, realtime, quota, metadata logging, and btree format transitions. Most behavioral changes here require tests that cover both extent-format and btree-format forks, delalloc and unwritten transitions, ENOSPC/low-space paths, reflink remap behavior, realtime files, and rmap/refcount interactions.
