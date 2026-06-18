# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` is the public interface for XFS block mapping operations. It declares the allocation argument structure, mapping flags, internal extent state flags, special startblock sentinels, exported bmap operations, deferred bmap intent structures, extent validation helpers, and query APIs.

## Key Types

- `struct xfs_bmalloca` carries all mutable state for one allocation operation, including transaction, inode, neighboring extents, logical offset, allocation length, selected physical block, btree cursor, in-core extent cursor, reservation totals, min-left constraints, EOF status, delayed allocation status, conversion status, allocation datatype, and bmapi flags.
- `enum xfs_bmap_intent_type` defines deferred map and unmap work items.
- `struct xfs_bmap_intent` records a deferred bmap operation: type, target fork, owner inode, optional group, and extent record.
- `xfs_bmap_query_range_fn` is the callback type for iterating bmap btree records.

## Mapping Flags

The `XFS_BMAPI_*` flags control mapping calls:

- `XFS_BMAPI_ENTIRE`: return whole extents rather than trimming to the request.
- `XFS_BMAPI_METADATA`: mapping metadata instead of user data.
- `XFS_BMAPI_ATTRFORK`: use the attribute fork.
- `XFS_BMAPI_PREALLOC`: allocate or represent unwritten preallocated extents.
- `XFS_BMAPI_CONTIG`: require one contiguous allocation.
- `XFS_BMAPI_CONVERT`: convert unwritten/written state rather than allocate normally.
- `XFS_BMAPI_ZERO`: zero newly allocated or converted extents.
- `XFS_BMAPI_REMAP`: map/unmap existing blocks without normal quota/refcount/free behavior.
- `XFS_BMAPI_COWFORK`: use the CoW fork.
- `XFS_BMAPI_NODISCARD`: skip online discard for freed extents.
- `XFS_BMAPI_NORMAP`: avoid rmap btree updates, used during reconstruction.
- `XFS_BMAPI_EXTSZALIGN`: attempt extent-size-hint alignment.

`xfs_bmapi_aflag` maps fork IDs to API flags, and `xfs_bmapi_whichfork` maps flags back to `XFS_DATA_FORK`, `XFS_ATTR_FORK`, or `XFS_COW_FORK`.

## Extent Sentinels and State Flags

- `DELAYSTARTBLOCK` denotes delayed allocation extents.
- `HOLESTARTBLOCK` denotes holes in returned mappings.
- `xfs_bmap_is_real_extent` detects allocated extents.
- `xfs_bmap_is_written_extent` narrows that to written real extents.
- `xfs_valid_startblock` rejects physical block zero except for realtime inodes.

Internal `BMAP_*` flags describe neighbor and fork state during extent update state machines. `xfs_bmap_fork_to_state` adds `BMAP_ATTRFORK` or `BMAP_COWFORK` as needed.

## Exported Operations

The header exposes:

- Mapping and allocation: `xfs_bmapi_read`, `xfs_bmapi_write`, `xfs_bmapi_remap`, `xfs_bmapi_convert_delalloc`.
- Unmapping: `xfs_bunmapi`, `xfs_bunmapi_range`.
- Fork conversion and attr fork setup: `xfs_bmap_local_to_extents_empty`, `xfs_bmap_local_to_extents`, `xfs_bmap_add_attrfork`.
- Extent deletion helpers for delayed and CoW forks.
- Unwritten conversion helper `xfs_bmap_add_extent_unwritten_real`.
- Logical range helpers: `xfs_bmap_first_unused`, `xfs_bmap_last_before`, `xfs_bmap_last_offset`, collapse/insert/split helpers.
- Allocation support: `xfs_bmapi_minleft`, `xfs_bmap_btalloc_low_space`, `xfs_bmap_worst_indlen`, `xfs_bmap_longest_free_extent`, `xfs_trim_extent`, `xfs_bmap_alloc_account`.
- Deferred mapping: `xfs_bmap_map_extent`, `xfs_bmap_unmap_extent`, `xfs_bmap_finish_one`.
- Validation and diagnostics: `xfs_bmap_validate_extent_raw`, `xfs_bmap_validate_extent`, `xfs_bmap_complain_bad_rec`.
- Query and hint helpers: `xfs_bmap_query_all`, `xfs_get_extsz_hint`, `xfs_get_cowextsz_hint`.
- Slab cache lifecycle for `xfs_bmap_intent_cache`.

## Dependencies and Consumers

This header is consumed by XFS file I/O, writeback, attribute, directory, reflink, truncate, repair/reconstruction, and deferred transaction code. It also couples bmap callers to bmap btree support through cursor arguments, but leaves btree layout details to `xfs_bmap_btree.h`.

## Research Notes

The flag combinations in this header define much of the valid behavioral surface. Callers must choose flags carefully: for example, `REMAP`, `PREALLOC`, `CONVERT`, `COWFORK`, `NORMAP`, and `ZERO` materially alter quota, rmap, refcount, and data exposure semantics.
