# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the core XFS block mapping implementation in `libxfs`. It manages logical file block to physical filesystem block mappings for inode forks, including data, attribute, and CoW forks. It covers reading mappings, allocating blocks, converting delayed allocations, converting unwritten extents, unmapping extents, remapping shared extents, shifting extents for collapse/insert range, splitting extents, and maintaining the extent-list versus bmap-btree fork formats.

This file is central to XFS metadata mutation. It updates incore extent maps, on-disk bmap btrees, inode block/extents accounting, quota counters, reverse mappings, refcount/reflink state, realtime metadata, and deferred bmap intents.

## Main Concepts

- XFS inode forks can store mappings in local, extent, or btree format.
- Real extents map file offsets to filesystem blocks.
- Delayed allocation extents use null startblocks that encode reserved indirect-block counts.
- Holes are represented externally with `HOLESTARTBLOCK`.
- Unwritten extents reserve disk blocks without exposing initialized file data as written.
- CoW fork extents are incore-only until remapped to the data fork.
- Bmap btrees are used when extent count exceeds inode inline extent capacity.
- Reverse mappings and refcount btrees are maintained alongside map changes.

## Key Data Flows

### Mapping Reads

`xfs_bmapi_read` validates fork format, loads btree extents into the incore map via `xfs_iread_extents`, walks the extent tree from the requested logical offset, synthesizes holes, trims returned records to the caller range, and coalesces adjacent returned mappings when possible.

Important helpers:

- `xfs_trim_extent`
- `xfs_bmapi_trim_map`
- `xfs_bmapi_update_map`
- `xfs_bmap_validate_ret` in debug builds

### Mapping Writes and Allocation

`xfs_bmapi_write` is the main allocation/conversion path. It walks existing mappings, decides whether a hole or delayed allocation requires real allocation, calls `xfs_bmapi_allocate`, optionally converts unwritten extents, and returns the resulting mappings.

Important helpers:

- `xfs_bmapi_allocate`
- `xfs_bmap_btalloc`
- `xfs_bmap_rtalloc` through external realtime allocation integration
- `xfs_bmap_add_extent_delay_real`
- `xfs_bmap_add_extent_hole_real`
- `xfs_bmap_add_extent_unwritten_real`
- `xfs_bmapi_convert_unwritten`
- `xfs_bmapi_finish`

Allocation chooses placement using:

- EOF and adjacent extent heuristics
- stripe alignment
- extent size hints
- CoW extent size hints
- filestream AG selection
- low-space fallback allocation
- realtime inode handling
- debug error tag forcing for minimum-length allocation

### Delayed Allocation Conversion

`xfs_bmapi_convert_delalloc` loops around `xfs_bmapi_convert_one_delalloc` until the returned iomap covers the requested byte offset. It converts an existing delayed allocation extent into real blocks, usually allocating from the start of the delalloc extent to create larger contiguous disk extents.

For page-cache writeback safety, data fork delayed allocations are allocated as unwritten extents first, then converted after I/O succeeds. CoW fork allocations are also initially unwritten and later remapped.

### Unmapping

`xfs_bunmapi` wraps `__xfs_bunmapi`, which walks mappings backwards over a requested range. It handles real extents, delayed extents, realtime alignment constraints, unwritten conversion for partial realtime extents, and btree-to-extents conversion after deletions.

Important helpers:

- `xfs_bmap_del_extent_real`
- `xfs_bmap_del_extent_delay`
- `xfs_bmap_del_extent_cow`
- `xfs_bmap_free_rtblocks`
- `xfs_bunmapi_range`

`xfs_bmap_del_extent_real` updates the incore extent list and optional bmap btree, removes rmaps, frees or refcount-decrements blocks, adjusts inode block counts, and updates quota counters.

### Remapping

`xfs_bmapi_remap` inserts an existing physical extent into a hole without normal allocation accounting. It is used by deferred bmap operations and reflink/remap flows. It asserts that the target range is a hole, updates inode accounting, inserts the extent, and performs any necessary btree-to-extents conversion.

### Extent Shifting and Splitting

The file implements higher-level file offset transformations:

- `xfs_bmap_collapse_extents` shifts extents left to fill a hole.
- `xfs_bmap_insert_extents` shifts extents right to create a hole.
- `xfs_bmap_can_insert_extents` checks for file offset overflow before right shifting.
- `xfs_bmap_split_extent` splits a real extent at a requested file offset.

Shift operations update bmap records and reverse mappings. Collapse can merge adjacent extents when shifted extents become contiguous.

### Fork Format Conversion

The file handles transitions among local, extent, and btree fork formats:

- `xfs_bmap_local_to_extents_empty`
- `xfs_bmap_local_to_extents`
- `xfs_bmap_extents_to_btree`
- `xfs_bmap_btree_to_extents`
- `xfs_bmap_add_attrfork`
- `xfs_bmap_add_attrfork_local`
- `xfs_bmap_add_attrfork_extents`
- `xfs_bmap_add_attrfork_btree`

`xfs_bmap_needs_btree` decides when extent format must become btree format. `xfs_bmap_wants_extents` decides when a small btree can collapse back to extent format.

### Btree Extent Loading

`xfs_iread_extents` loads records from a btree-format fork into the incore extent cache. It uses `xfs_btree_visit_blocks` and `xfs_iread_bmbt_block`, validates each record, inserts it into the incore extent map, and clears `if_needextents` with release semantics.

If loading fails, the fork extent cache is destroyed and the fork is marked sick when appropriate.

### Deferred Bmap Intents

The file defines and processes deferred mapping operations:

- `xfs_bmap_map_extent`
- `xfs_bmap_unmap_extent`
- `xfs_bmap_finish_one`
- `xfs_bmap_intent_init_cache`
- `xfs_bmap_intent_destroy_cache`

Deferred intents skip holes, delayed allocations, and unsupported forks. Finish processing remaps or unmaps one extent at a time.

## Important Validation and Integrity Checks

The code aggressively validates metadata state:

- `xfs_bmap_validate_extent_raw` verifies file extent ranges, physical block ranges, realtime ranges, and unwritten-state restrictions.
- `xfs_bmap_validate_extent` applies inode context.
- `xfs_bmap_complain_bad_rec` emits detailed corruption warnings.
- Debug-only btree leaf checks verify ordering and duplicate child pointers.
- Many paths mark bmap btrees or forks sick on corruption.
- Shutdown state returns `-EIO`.
- Error tags can force corruption or allocation behavior in debug/test builds.

## Accounting Responsibilities

Allocation, conversion, and deletion paths update:

- `ip->i_nblocks`
- `ip->i_delayed_blks`
- fork extent counts
- delayed allocation global counters
- free data blocks
- free realtime extents
- quota block or realtime block counters
- transaction inode logging flags
- btree cursor allocated-block counters
- reverse map and refcount side structures

`xfs_bmap_alloc_account` centralizes much of the post-allocation inode/quota accounting, with special treatment for CoW fork allocations.

## Dependencies and Collaborators

Major collaborators include:

- `xfs_bmap_btree.c` and `xfs_bmap_btree.h` for bmap btree operations.
- `xfs_iext_*` incore extent list APIs.
- `xfs_alloc_*` allocation APIs.
- `xfs_rmap_*` reverse mapping updates.
- `xfs_refcount_*` reflink and CoW accounting.
- `xfs_rtbitmap`, `xfs_rtgroup`, and realtime allocation/free logic.
- transaction and quota code.
- directory and symlink conversion helpers for local-to-remote fork conversion.
- `iomap` for writeback mapping returns.

## Notable Invariants

- CoW fork does not use bmap btree format conversion here.
- Attribute fork cannot carry unwritten extents.
- Returned maps from `xfs_bmapi_read/write` must be ordered and contiguous in returned logical range.
- Real extent merges require logical contiguity, physical contiguity, matching state, max length limits, and realtime group compatibility.
- Delayed allocation records carry indirect reservation state in the encoded null startblock.
- Btree mutations are mirrored in the incore extent cache.
- Reverse mappings must be removed and re-added when file offsets shift.
- Realtime extents often cannot be partially freed unless aligned to realtime extent boundaries.

## Research Notes

This file is the behavioral hub for XFS extent mapping. The most important maintenance risk is that each mapping mutation has several synchronized side effects: incore extents, btree records, inode counters, quota, reverse mapping, refcount/reflink state, realtime metadata, and transaction logging must remain consistent. The many switch statements over left/right fill and contiguity states encode the extent merge/split matrix and are the highest-density correctness logic in the file.
