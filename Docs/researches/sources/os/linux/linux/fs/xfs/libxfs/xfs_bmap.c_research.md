# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the main XFS inode block mapping implementation. It translates file-relative block offsets to filesystem blocks, allocates and frees mapped extents, converts delayed allocation and unwritten extents, maintains inode fork extent state, and coordinates those changes with bmap btrees, reverse mappings, refcount/reflink, quotas, realtime allocation, zoned realtime accounting, transaction logging, and deferred bmap intents.

This file is the behavioral center of XFS extent mapping. Almost every metadata-changing mapping operation must keep the in-core extent tree, optional bmap btree, inode counters, quota reservations, rmap/refcount state, free-space accounting, and transaction log flags synchronized.

## Major Responsibilities

- Compute maximum bmap btree levels and default attribute fork offsets.
- Convert inode forks between local, extent, and btree formats.
- Load btree-format fork extents into the in-core extent cache.
- Query first unused logical blocks, last mapped blocks, and last extents.
- Read mappings without allocation via `xfs_bmapi_read`.
- Allocate or convert mappings via `xfs_bmapi_write`.
- Convert delayed allocation extents for writeback via `xfs_bmapi_convert_delalloc`.
- Insert remapped extents into holes via `xfs_bmapi_remap`.
- Remove extents via `xfs_bunmapi` and `xfs_bunmapi_range`.
- Delete/split delayed, CoW, and real extents.
- Shift and split extents for collapse range, insert range, and extent splitting.
- Record and finish deferred bmap map/unmap intents.
- Validate extent records and expose btree query helpers.
- Calculate data and CoW extent size hints.

## Key Data Flows

### Fork Format Conversion

The file handles transitions among inode fork formats:

- `xfs_bmap_local_to_extents_empty`
- `xfs_bmap_local_to_extents`
- `xfs_bmap_extents_to_btree`
- `xfs_bmap_btree_to_extents`
- `xfs_bmap_add_attrfork`
- `xfs_bmap_add_attrfork_local`
- `xfs_bmap_add_attrfork_extents`
- `xfs_bmap_add_attrfork_btree`

`xfs_bmap_needs_btree` decides when a non-CoW extent-format fork exceeds inline capacity and must become btree format. `xfs_bmap_wants_extents` decides when a shallow btree can collapse back to extent format.

Conversion is not just a representation change. It allocates or frees bmap btree blocks, adjusts `i_nblocks`, updates quota, initializes or destroys inode-root btree data, and logs the correct inode fork fields.

### Extent Cache Loading

`xfs_iread_extents` loads btree-format fork records into the in-core extent cache. It initializes a bmap btree cursor, visits record blocks through the generic btree layer, decodes each `xfs_bmbt_rec`, validates it with `xfs_bmap_validate_extent`, inserts it into the in-core extent tree, and clears `if_needextents` with release semantics.

If loading fails, the extent cache is destroyed and the fork is marked sick when corruption-like errors are detected.

### Mapping Reads

`xfs_bmapi_read` maps logical file blocks without allocating storage. It validates fork state, loads btree extents if needed, walks the in-core extent tree from the requested offset, synthesizes hole mappings, trims records to the caller range unless `XFS_BMAPI_ENTIRE` is set, and coalesces adjacent returned mappings where possible.

Important helpers:

- `xfs_trim_extent`
- `xfs_bmapi_trim_map`
- `xfs_bmapi_update_map`
- `xfs_bmap_validate_ret` in debug builds

Returned mappings use `HOLESTARTBLOCK` for holes and `DELAYSTARTBLOCK` for delayed allocation records.

### Mapping Writes and Allocation

`xfs_bmapi_write` is the primary write mapping path. It walks existing mappings over the requested logical range, decides whether a hole or delayed allocation requires physical allocation, calls `xfs_bmapi_allocate`, optionally converts unwritten extents, records mappings to return to the caller, and finally collapses btree forks back to extent format if possible.

Key helpers:

- `xfs_bmapi_allocate`
- `xfs_bmap_btalloc`
- `xfs_bmap_rtalloc` through realtime allocation integration
- `xfs_bmap_add_extent_delay_real`
- `xfs_bmap_add_extent_hole_real`
- `xfs_bmap_add_extent_unwritten_real`
- `xfs_bmapi_convert_unwritten`
- `xfs_bmapi_finish`

Allocation selection considers EOF placement, adjacent extents, stripe alignment, extent size hints, CoW extent size hints, filestream AG selection, low-space fallback, realtime inodes, and debug minlen error injection.

### Delayed Allocation Conversion

`xfs_bmapi_convert_delalloc` repeatedly calls `xfs_bmapi_convert_one_delalloc` until the returned iomap covers the requested byte offset. Conversion intentionally starts at the beginning of the current delayed allocation extent to encourage large contiguous physical extents.

For writeback safety, data fork delayed allocations are allocated as unwritten extents and later converted after I/O succeeds. CoW fork allocations are also created unwritten and later remapped to the data fork.

### Extent State Machines

The densest correctness logic is in the add/convert/delete extent helpers. They compute state bits such as left/right fill, left/right contiguity, delayed neighbors, and fork type, then execute a case matrix that updates both the in-core extent list and optional bmap btree.

Important cases include:

- delayed allocation to real extent
- hole to real extent
- unwritten to written conversion
- written to unwritten conversion
- full deletion
- deletion from the left or right edge
- deletion from the middle, which splits one extent into two
- three-way merges when both neighbors are contiguous

Merges require logical adjacency, physical adjacency, matching extent state, maximum bmap extent length limits, and compatible realtime group placement.

### Unmapping

`xfs_bunmapi` wraps `__xfs_bunmapi`, which walks mappings backwards over the requested range. It removes delayed, CoW, and real extents differently and handles realtime alignment restrictions specially. Partial realtime extent deletion may convert written ranges to unwritten rather than freeing sub-realtime-extent fragments.

Key helpers:

- `xfs_bmap_del_extent_delay`
- `xfs_bmap_del_extent_cow`
- `xfs_bmap_del_extent_real`
- `xfs_bmap_free_rtblocks`
- `xfs_bunmapi_range`

`xfs_bmap_del_extent_real` removes rmaps, decreases refcounts for reflinked data fork extents, frees normal or realtime extents, applies no-discard flags for unwritten extents or explicit `NODISCARD`, adjusts `i_nblocks`, and updates quota unless the operation is a remap-only unmap.

Mainline-specific realtime behavior includes routing realtime frees through deferred free intents when rtgroups support rmap/refcount ordering, while legacy realtime frees still use `xfs_rtfree_blocks`.

### Remapping

`xfs_bmapi_remap` inserts an existing physical extent into a hole, primarily for reflink/remap and deferred bmap intent processing. It asserts that the destination range is a hole, adjusts inode block and delayed-block accounting, optionally creates an unwritten extent, inserts the mapping through the normal hole-to-real helper, and performs btree-to-extents conversion if possible.

`XFS_BMAPI_NORMAP` allows reconstruction paths to skip rmap updates.

### Extent Shifting and Splitting

The file supports higher-level file offset transformations:

- `xfs_bmap_collapse_extents` shifts extents left to fill a removed range.
- `xfs_bmap_insert_extents` shifts extents right to create a hole.
- `xfs_bmap_can_insert_extents` checks for file offset overflow before right shifting.
- `xfs_bmap_split_extent` splits one real extent into two at a file offset.

Shift operations update both bmap records and reverse mappings. Left shifts can merge with the preceding extent when logical and physical adjacency allow it. Right shifts warn if they encounter extents that would have been mergeable because insert-range should not create that condition.

### Deferred Bmap Intents

The file defines and processes deferred mapping operations:

- `xfs_bmap_map_extent`
- `xfs_bmap_unmap_extent`
- `xfs_bmap_finish_one`
- `xfs_bmap_intent_init_cache`
- `xfs_bmap_intent_destroy_cache`

Deferred bmap intents ignore unsupported forks, holes, and delayed allocations. Finish processing remaps or unmaps one extent at a time and uses an error tag hook for fault injection.

## Important Validation and Integrity Checks

- `xfs_bmap_validate_extent_raw` verifies file extent ranges, physical block ranges, realtime ranges, and unwritten-state restrictions.
- `xfs_bmap_validate_extent` adds inode context.
- `xfs_bmap_complain_bad_rec` reports corrupted bmap records with inode and fork context.
- Debug code verifies btree leaf order and duplicate child pointers.
- Many corruption branches mark btrees or forks sick before returning `-EFSCORRUPTED`.
- Shutdown state returns `-EIO`.
- Error tags inject bmap format, allocation, and finish-one failures for testing.

## Accounting Responsibilities

Mapping changes can update:

- `ip->i_nblocks`
- `ip->i_delayed_blks`
- fork extent counts
- global delayed allocation counters
- free data blocks
- free realtime extents
- zoned realtime availability
- quota block or realtime block counters
- transaction inode log flags
- btree cursor allocated-block counters
- reverse mapping records
- refcount records for reflink and CoW

`xfs_bmap_alloc_account` centralizes much post-allocation accounting. CoW fork allocations are treated as in-core quota reservations until remapped to the data fork.

## Notable Invariants

- CoW forks are not converted to bmap btree format through these helpers.
- Attribute fork extents cannot be unwritten.
- Returned mappings from `xfs_bmapi_read` and `xfs_bmapi_write` are ordered and contiguous in logical range.
- Delayed allocation records encode indirect block reservation in null startblocks.
- Btree mutations are mirrored in the in-core extent cache.
- Realtime extents often cannot be partially freed unless aligned to realtime extent boundaries.
- Rmap updates must track file offset changes during shifts and conversions.
- Data exposure safety requires newly allocated writeback extents to be unwritten until I/O completion.

## Dependencies and Collaborators

Major collaborators include:

- `xfs_bmap_btree.c` and `xfs_bmap_btree.h` for bmap btree operations.
- `xfs_iext_*` for in-core extent storage.
- `xfs_alloc_*` and filestream allocation for block placement.
- `xfs_rtbitmap`, `xfs_rtgroup`, and zoned allocation code for realtime files.
- `xfs_rmap_*` for reverse mappings.
- `xfs_refcount_*` for reflink and CoW accounting.
- transaction, quota, health, and error-tag subsystems.
- symlink and directory conversion helpers for local-to-remote fork transitions.
- iomap conversion helpers for writeback mappings.

## Research Notes

This file is high-risk because each mapping mutation has multiple synchronized side effects. The largest maintenance hazards are the extent merge/split state machines, delayed allocation reservation redistribution, realtime partial-free behavior, btree format transitions, and remap paths that intentionally suppress normal free/quota/refcount behavior.
